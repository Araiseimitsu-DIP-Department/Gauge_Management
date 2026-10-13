from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import psycopg
from app.config.app_settings import load_app_settings
from scripts.postgres_sequence import read_loan_sequence, synchronize_loan_sequence, quote_identifier, LENDING_TABLE, LOCK_TIMEOUT

logger = logging.getLogger(__name__)


def data_fingerprint(cursor, schema: str) -> tuple:
    table = f"{quote_identifier(schema)}.{quote_identifier(LENDING_TABLE)}"
    cursor.execute(
        f"SELECT COUNT(*), MAX(id), md5(string_agg(md5(row_to_json(t)::text), '' ORDER BY id)) FROM {table} t"
    )
    return cursor.fetchone()


def main() -> int:
    parser = argparse.ArgumentParser(description="貸出IDの採番状態を確認し、明示指定時だけ補正します。")
    parser.add_argument("--apply", action="store_true", help="採番値の補正を実行。通常は確認のみ。")
    args = parser.parse_args()
    settings = load_app_settings(PROJECT_ROOT / ".env").postgres_db
    if not settings.is_configured:
        logger.error("PostgreSQL接続設定がありません。")
        return 2
    try:
        with psycopg.connect(settings.connection_url, connect_timeout=5) as connection:
            with connection.cursor() as cursor:
                if not args.apply:
                    cursor.execute("SET TRANSACTION READ ONLY")
                    state = read_loan_sequence(cursor, settings.schema)
                    print(json.dumps({"最大ID": state.maximum_id, "次回ID": state.next_id, "補正必要": state.needs_repair}, ensure_ascii=False))
                    return 0
                cursor.execute("SELECT set_config('lock_timeout', %s, true)", (LOCK_TIMEOUT,))
                table = f"{quote_identifier(settings.schema)}.{quote_identifier(LENDING_TABLE)}"
                cursor.execute(f"LOCK TABLE {table} IN SHARE ROW EXCLUSIVE MODE")
                original = data_fingerprint(cursor, settings.schema)
                before, after = synchronize_loan_sequence(cursor, settings.schema)
                if original != data_fingerprint(cursor, settings.schema):
                    raise RuntimeError("貸出データの一致確認に失敗しました。")
                report = {
                    "補正前次回ID": before.next_id, "補正後次回ID": after.next_id,
                    "既存最大ID": after.maximum_id, "貸出件数": original[0], "既存データ一致": True,
                }
            connection.commit()
        logger.info("貸出シーケンスの補正とデータ一致確認が完了しました。")
        print(json.dumps(report, ensure_ascii=False))
    except Exception as exc:
        # 接続実値や業務データをログへ露出させない。
        logger.error("採番確認・補正に失敗しました: %s", type(exc).__name__)
        return 1
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(main())
