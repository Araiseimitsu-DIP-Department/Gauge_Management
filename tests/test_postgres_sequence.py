from dataclasses import replace
import unittest
from unittest.mock import MagicMock, Mock, patch
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

from scripts.postgres_sequence import LoanSequenceState, quote_identifier, synchronize_loan_sequence


class LoanSequenceTests(unittest.TestCase):
    def setUp(self):
        self.state = LoanSequenceState("public", "loan_id_seq", 33836, 33834, True, 1, 1, 9223372036854775807, False)

    def test_detects_behind_and_uncalled_sequence(self):
        self.assertTrue(self.state.needs_repair)
        self.assertEqual(self.state.next_id, 33835)
        uncalled = replace(self.state, last_value=33836, is_called=False)
        self.assertTrue(uncalled.needs_repair)
        self.assertEqual(uncalled.next_id, 33836)

    def test_empty_or_ahead_sequence_needs_no_repair(self):
        self.assertFalse(replace(self.state, maximum_id=None).needs_repair)
        self.assertFalse(replace(self.state, last_value=33836).needs_repair)
        self.assertFalse(replace(self.state, last_value=34000).needs_repair)

    def test_repair_locks_and_advances_to_unused_id(self):
        cursor = Mock()
        repaired = replace(self.state, last_value=33837, is_called=False)
        with patch("scripts.postgres_sequence.read_loan_sequence", side_effect=[self.state, self.state, repaired]):
            before, after = synchronize_loan_sequence(cursor, "public")
        self.assertEqual(before.next_id, 33835)
        self.assertEqual(after.next_id, 33837)
        queries = [call.args[0] for call in cursor.execute.call_args_list]
        self.assertIn('LOCK TABLE "public"."pin_gauge_lending" IN SHARE ROW EXCLUSIVE MODE', queries)
        self.assertIn('ALTER SEQUENCE "public"."loan_id_seq" CACHE 1', queries)
        self.assertIn('ALTER SEQUENCE "public"."loan_id_seq" RESTART WITH 33837', queries)
        self.assertFalse(any("setval" in query or "nextval" in query for query in queries))

    def test_rechecks_after_sequence_lock_and_never_moves_back(self):
        cursor = Mock()
        ahead = replace(self.state, last_value=34000)
        with patch("scripts.postgres_sequence.read_loan_sequence", side_effect=[self.state, ahead, ahead]):
            synchronize_loan_sequence(cursor, "public")
        self.assertFalse(any("RESTART" in call.args[0] for call in cursor.execute.call_args_list))

    def test_rejects_nonstandard_sequence(self):
        for state in (replace(self.state, increment=2), replace(self.state, cycle=True)):
            with self.subTest(state=state), patch("scripts.postgres_sequence.read_loan_sequence", return_value=state):
                with self.assertRaises(ValueError):
                    synchronize_loan_sequence(Mock(), "public")

    def test_rejects_exhausted_sequence(self):
        exhausted = replace(self.state, maximum_value=33836)
        with patch("scripts.postgres_sequence.read_loan_sequence", return_value=exhausted):
            with self.assertRaises(ValueError):
                synchronize_loan_sequence(Mock(), "public")

    def test_detects_failed_post_repair_check(self):
        with patch("scripts.postgres_sequence.read_loan_sequence", return_value=self.state):
            with self.assertRaises(RuntimeError):
                synchronize_loan_sequence(Mock(), "public")

    def test_quotes_schema_identifiers(self):
        self.assertEqual(quote_identifier('a"b'), '"a""b"')

    def test_query_error_is_not_wrapped_as_connection_error(self):
        from app.config.db_settings import PostgresDbSettings
        from app.infrastructure.postgres.connection import open_postgres_connection
        with patch("psycopg.connect"):
            with self.assertRaisesRegex(ValueError, "SQL処理失敗"):
                with open_postgres_connection(PostgresDbSettings("postgresql://test")):
                    raise ValueError("SQL処理失敗")


class LegacyAppendTests(unittest.TestCase):
    def load_migration(self):
        path = Path(__file__).resolve().parents[1] / "docs/pingauge_management_db/migrate_access_to_postgres_pingauge_management_db.py"
        psycopg2 = ModuleType("psycopg2")
        psycopg2.connect = MagicMock()
        extras = ModuleType("psycopg2.extras")
        extras.execute_values = Mock()
        dotenv = ModuleType("dotenv")
        dotenv.dotenv_values = Mock()
        spec = importlib.util.spec_from_file_location("legacy_migration_under_test", path)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {
            spec.name: module, "psycopg2": psycopg2,
            "psycopg2.extras": extras, "dotenv": dotenv, "pyodbc": ModuleType("pyodbc"),
        }):
            spec.loader.exec_module(module)
        return module

    def test_append_synchronizes_before_commit(self):
        migration = self.load_migration()
        connection = migration.psycopg2.connect.return_value
        connection.cursor.return_value.__enter__.return_value.fetchone.return_value = ("public.seq",)
        mapping = SimpleNamespace(postgres_name="pin_gauge_lending")
        with patch.object(migration, "connect_access"), patch.object(migration, "append_missing_rows_for_table"), patch.object(migration, "synchronize_loan_sequence") as sync:
            events = Mock()
            events.attach_mock(sync, "sync")
            events.attach_mock(connection.commit, "commit")
            migration.append_missing_rows("unused", Path("unused"), [mapping], "public", 1000)
        self.assertEqual([call[0] for call in events.mock_calls], ["sync", "commit"])

    def test_failed_synchronization_rolls_back_append(self):
        migration = self.load_migration()
        connection = migration.psycopg2.connect.return_value
        connection.cursor.return_value.__enter__.return_value.fetchone.return_value = ("public.seq",)
        mapping = SimpleNamespace(postgres_name="pin_gauge_lending")
        with patch.object(migration, "connect_access"), patch.object(migration, "append_missing_rows_for_table"), patch.object(migration, "synchronize_loan_sequence", side_effect=ValueError("補正失敗")):
            with self.assertRaises(ValueError):
                migration.append_missing_rows("unused", Path("unused"), [mapping], "public", 1000)
        connection.rollback.assert_called_once()
        connection.commit.assert_not_called()

    def test_legacy_bigint_append_is_preserved(self):
        migration = self.load_migration()
        connection = migration.psycopg2.connect.return_value
        connection.cursor.return_value.__enter__.return_value.fetchone.return_value = (None,)
        mapping = SimpleNamespace(postgres_name="pin_gauge_lending")
        with patch.object(migration, "connect_access"), patch.object(migration, "append_missing_rows_for_table"), patch.object(migration, "synchronize_loan_sequence") as sync, self.assertLogs(level="WARNING"):
            migration.append_missing_rows("unused", Path("unused"), [mapping], "public", 1000)
        sync.assert_not_called()
        connection.commit.assert_called_once()
