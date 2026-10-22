from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app.config.ui_preferences import load_theme, save_theme
from app.version import APP_VERSION
from app.webview.backend import WebviewBridge
from app.webview.frontend import build_html


class UiPreferencesTests(unittest.TestCase):
    def test_missing_and_invalid_preferences_use_light(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ui-theme.txt"
            self.assertEqual(load_theme(path), "light")
            path.write_text("unknown", encoding="utf-8")
            with self.assertLogs("app.config.ui_preferences", level="WARNING"):
                self.assertEqual(load_theme(path), "light")
            path.write_bytes(b"\xff")
            with self.assertLogs("app.config.ui_preferences", level="WARNING"):
                self.assertEqual(load_theme(path), "light")

    def test_theme_survives_reload_and_invalid_update_preserves_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "preferences" / "ui-theme.txt"
            for theme in ("dark", "light"):
                save_theme(theme, path)
                self.assertEqual(load_theme(path), theme)
            for invalid in ("", "DARK", None, [], {}):
                with self.assertRaises(ValueError):
                    save_theme(invalid, path)
                self.assertEqual(load_theme(path), "light")
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_bridge_success_invalid_payload_and_write_failure(self):
        bridge = WebviewBridge(settings=None, lending_service=None, operation_service=None, master_service=None)
        with patch("app.webview.backend.save_theme") as save:
            self.assertEqual(bridge.save_theme({"theme": "dark"}), {"ok": True, "data": {"theme": "dark"}})
            save.assert_called_once_with("dark")
        with self.assertLogs("app.webview.backend", level="ERROR"):
            self.assertFalse(bridge.save_theme(None)["ok"])
        with patch("app.webview.backend.save_theme", side_effect=OSError("書込み不可")):
            with self.assertLogs("app.webview.backend", level="ERROR"):
                result = bridge.save_theme({"theme": "dark"})
            self.assertFalse(result["ok"])
            self.assertEqual(result["message"], "書込み不可")

    def test_failed_replace_preserves_previous_theme_and_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ui-theme.txt"
            save_theme("light", path)
            with patch.object(Path, "replace", side_effect=OSError("保存失敗")):
                with self.assertRaises(OSError):
                    save_theme("dark", path)
            self.assertEqual(load_theme(path), "light")
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_html_injects_saved_theme_and_version(self):
        with patch("app.webview.frontend.load_theme", return_value="dark"):
            html = build_html("ピンゲージ管理")
        self.assertIn('let displayTheme = "dark"', html)
        self.assertIn(f'class="app-version">v{APP_VERSION}', html)
        self.assertNotIn("__APP_SCRIPT__", html)
        self.assertNotIn("__INITIAL_THEME__", html)


if __name__ == "__main__":
    unittest.main()
