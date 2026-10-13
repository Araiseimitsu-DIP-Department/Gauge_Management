# DBアクセス

PostgreSQL実装は `app/infrastructure/postgres/`、Access実装は `app/infrastructure/access/`。
`repository_factory.py` が `DB_BACKEND` により選ぶ。PostgreSQL失敗時のAccessフォールバックはない。
Access専用実装はAccess選択時にだけインポートする。

PostgreSQLは `psycopg[binary]`、Accessは `pyodbc` とWindowsのAccess ODBCドライバーを必要とする。
PostgreSQLのURLは `POSTGRES_CONNECTION_URL` を優先し、`DATABASE_URL` を代替とする。
`POSTGRES_SCHEMA` は未指定時 `public`。テーブル・カラム対応はREADME、DDLは `database/postgresql/` を参照。

PostgreSQL接続は遅延インポートしたpsycopgの接続コンテキストを使用する。
更新メソッドはcommitし、異常終了時は接続コンテキストによるロールバックに依存する。
貸出IDはDBのシーケンスが採番し、アプリからINSERT時に指定しない。新規DDLはIDENTITY、現在の実DBはDEFAULT nextval構成。
ID明示投入後の採番確認・補正と今回の不整合調査は [loan-sequence.md](loan-sequence.md) を参照。

貸出登録・編集・削除、返却、確認、マスタ保存・削除、部署補正がデータを変更する。
画面初期化でも部署補正が実行されるため、実DBを使うGUI確認には更新への配慮が必要。
データ更新の共通検証手順は `.agents/skills/development-workflow/references/data-update-verification.md`。

移行スクリプトの `--apply-schema`、`--truncate`、制約・索引追加は検証用には実行しない。
移行詳細は既存の [postgresql-migration.md](postgresql-migration.md) を参照。移行履歴は現在のDB状態を保証しない。
