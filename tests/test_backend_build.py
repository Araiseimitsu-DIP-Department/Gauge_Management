from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from app.config.app_settings import load_app_settings
from app.config.db_settings import load_postgres_db_settings
from app.shared.errors import ConfigurationError, DataAccessError
from app.infrastructure.postgres.connection import open_postgres_connection

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_python(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code], cwd=PROJECT_ROOT,
        capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
    )


class BackendTests(unittest.TestCase):
    def test_postgres_startup_without_access_imports(self):
        code = '''
import importlib.abc
import sys
from unittest.mock import patch
class BlockAccess(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "pyodbc" or fullname.startswith("app.infrastructure.access"):
            raise AssertionError("Accessが読み込まれました: " + fullname)
sys.meta_path.insert(0, BlockAccess())
from app.config.app_settings import AppSettings
from app.config.db_settings import AccessDbSettings, PostgresDbSettings
from app.infrastructure.repository_factory import build_repository_bundle
from app.shared.errors import ConfigurationError, DataAccessError
from app.infrastructure.postgres.connection import open_postgres_connection
from app import bootstrap
settings = AppSettings("test", "local", "postgres", AccessDbSettings(None), PostgresDbSettings(None))
bundle = build_repository_bundle(settings)
assert all(type(repo).__name__.startswith("Postgres") for repo in (bundle.lending, bundle.master, bundle.operation))
with patch.object(bootstrap, "load_app_settings", return_value=settings), patch.object(bootstrap.webview, "create_window") as window, patch.object(bootstrap.webview, "start"):
    assert bootstrap.run() == 0
    window.assert_called_once()
try:
    with open_postgres_connection(settings.postgres_db):
        pass
except ConfigurationError:
    pass
else:
    raise AssertionError("未設定の接続が成功しました")
assert "pyodbc" not in sys.modules
'''
        result = run_python(code)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_frozen_default_and_explicit_access(self):
        with tempfile.TemporaryDirectory() as directory:
            env = Path(directory) / ".env"
            with patch.object(sys, "frozen", True, create=True):
                self.assertEqual(load_app_settings(env).database_backend, "postgres")
                env.write_text("DB_BACKEND=access\n", encoding="utf-8")
                self.assertEqual(load_app_settings(env).database_backend, "access")

    def test_access_without_driver_reports_configuration_error(self):
        code = '''
import importlib.abc
import sys
class BlockDriver(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "pyodbc":
            raise ModuleNotFoundError("pyodbcがありません")
sys.meta_path.insert(0, BlockDriver())
from app.config.app_settings import AppSettings
from app.config.db_settings import AccessDbSettings, PostgresDbSettings
from app.infrastructure.repository_factory import build_repository_bundle
from app.shared.errors import ConfigurationError
settings = AppSettings("test", "local", "access", AccessDbSettings(None), PostgresDbSettings(None))
try:
    build_repository_bundle(settings)
except ConfigurationError as exc:
    assert "pyodbc" in str(exc)
else:
    raise AssertionError("Accessドライバー不在が通知されませんでした")
'''
        result = run_python(code)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_connection_url_priority(self):
        settings = load_postgres_db_settings({
            "POSTGRES_CONNECTION_URL": "postgresql://primary",
            "DATABASE_URL": "postgresql://secondary",
        })
        self.assertEqual(settings.connection_url, "postgresql://primary")
        self.assertEqual(load_postgres_db_settings({"DATABASE_URL": "fallback"}).connection_url, "fallback")

    def test_invalid_backend_rejected(self):
        from app.config.app_settings import AppSettings
        from app.config.db_settings import AccessDbSettings, PostgresDbSettings
        from app.infrastructure.repository_factory import build_repository_bundle
        settings = AppSettings("test", "local", "invalid", AccessDbSettings(None), PostgresDbSettings(None))
        with self.assertLogs("app.infrastructure.repository_factory", level="ERROR"):
            with self.assertRaises(ConfigurationError):
                build_repository_bundle(settings)

    def test_access_still_selectable(self):
        from app.config.app_settings import AppSettings
        from app.config.db_settings import AccessDbSettings, PostgresDbSettings
        from app.infrastructure.repository_factory import build_repository_bundle
        import importlib.util
        if importlib.util.find_spec("pyodbc") is None:
            self.skipTest("Access用の任意依存pyodbcが未導入です。")
        settings = AppSettings("test", "local", "access", AccessDbSettings(None), PostgresDbSettings(None))
        bundle = build_repository_bundle(settings)
        self.assertIn("access", type(bundle.master).__module__)

    def test_connection_failure_does_not_fallback(self):
        from app.config.db_settings import PostgresDbSettings
        with patch("psycopg.connect", side_effect=RuntimeError("接続失敗")) as connect:
            with self.assertRaises(DataAccessError):
                with open_postgres_connection(PostgresDbSettings("postgresql://test")):
                    pass
        connect.assert_called_once_with("postgresql://test")


class BuildProfileTests(unittest.TestCase):
    def run_spec(self, root: Path, backend: str | None = None):
        namespace = {"SPECPATH": str(root), "Analysis": lambda *args, **kwargs: type(
            "AnalysisResult", (), {
                "pure": [], "scripts": [], "binaries": [],
                "datas": kwargs["datas"], "excludes": kwargs["excludes"],
            }
        )(), "PYZ": lambda *args: None, "EXE": lambda *args, **kwargs: None}
        with patch.dict(os.environ, {}, clear=True):
            if backend is not None:
                os.environ["PINGAUGE_BUILD_BACKEND"] = backend
            exec(compile((PROJECT_ROOT / "PinGaugeMgmt.spec").read_text(encoding="utf-8"), "PinGaugeMgmt.spec", "exec"), namespace)
        return namespace

    def test_default_profile_filters_access_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text(
                "DB_BACKEND=postgres\nACCESS_DB_DIRECTORY=unused\nPOSTGRES_CONNECTION_URL=postgresql://test\nOTHER=unused\n",
                encoding="utf-8",
            )
            namespace = self.run_spec(root)
            config = namespace["build_env_path"].read_text(encoding="utf-8")
            self.assertIn("DB_BACKEND=postgres", config)
            self.assertIn("POSTGRES_CONNECTION_URL=postgresql://test", config)
            self.assertNotIn("ACCESS_DB_DIRECTORY", config)
            self.assertNotIn("OTHER", config)
            self.assertIn("pyodbc", namespace["a"].excludes)
            self.assertIn("app.infrastructure.access", namespace["a"].excludes)
            self.assertNotIn("app.repositories", namespace["a"].excludes)

    def test_missing_env_still_embeds_explicit_postgres(self):
        with tempfile.TemporaryDirectory() as directory:
            namespace = self.run_spec(Path(directory))
            self.assertEqual(namespace["build_env_path"].read_text(encoding="utf-8"), "DB_BACKEND=postgres\n")

    def test_mismatched_backend_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text("DB_BACKEND=access\n", encoding="utf-8")
            with self.assertLogs(level="ERROR"):
                with self.assertRaises(ValueError):
                    self.run_spec(root)

    def test_access_profile_preserves_access_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text("DB_BACKEND=access\nACCESS_DB_DIRECTORY=kept\nDATABASE_URL=unused\n", encoding="utf-8")
            namespace = self.run_spec(root, "access")
            config = namespace["build_env_path"].read_text(encoding="utf-8")
            self.assertIn("ACCESS_DB_DIRECTORY=kept", config)
            self.assertNotIn("DATABASE_URL", config)
            self.assertEqual(namespace["a"].excludes, [])

    def test_invalid_profile_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertLogs(level="ERROR"):
                with self.assertRaises(ValueError):
                    self.run_spec(Path(directory), "invalid")


if __name__ == "__main__":
    unittest.main()
