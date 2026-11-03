"""貸出検索と選択返却のSQL条件を、DBへ接続せずに確認する。"""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class LendingSearchScopeTests(unittest.TestCase):
    def test_loan_search_includes_return_box_and_excludes_confirmed(self):
        access_sql = (
            ROOT / "app/infrastructure/access/repositories/lending_repository.py"
        ).read_text(encoding="utf-8")
        postgres_sql = (
            ROOT / "app/infrastructure/postgres/repositories/lending_repository.py"
        ).read_text(encoding="utf-8")

        self.assertIn("(t_貸出.完了フラグ IS NULL OR t_貸出.完了フラグ = 'N')", access_sql)
        self.assertIn(
            """WHERE (l.\"completion_flag\" IS NULL OR l.\"completion_flag\" = 'N')""",
            postgres_sql,
        )
        self.assertNotIn("完了フラグ = 'Y'", access_sql)
        self.assertNotIn("completion_flag\" = 'Y'", postgres_sql)

    def test_selected_return_updates_only_open_loans(self):
        access_sql = (
            ROOT / "app/infrastructure/access/repositories/operation_repository.py"
        ).read_text(encoding="utf-8")
        postgres_sql = (
            ROOT / "app/infrastructure/postgres/repositories/operation_repository.py"
        ).read_text(encoding="utf-8")

        self.assertIn("def return_selected_loans", access_sql)
        self.assertIn("AND 返却日 IS NULL", access_sql)
        self.assertIn("AND 完了フラグ IS NULL", access_sql)
        self.assertIn("def return_selected_loans", postgres_sql)
        self.assertIn('AND "returned_date" IS NULL', postgres_sql)
        self.assertIn('AND "completion_flag" IS NULL', postgres_sql)


if __name__ == "__main__":
    unittest.main()
