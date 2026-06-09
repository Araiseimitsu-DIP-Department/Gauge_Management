# PostgreSQL Migration Notes

## Target

- Host: `192.168.1.120`
- Database: `pingauge_management`
- Schema: `public`

## Run Order

1. Create database `pingauge_management` in TablePlus or psql.
2. Run `001_schema.sql`.
3. Import data using `scripts/migrate_access_to_postgres.py` or `010_import_from_csv.sql`.
4. Run `020_validation.sql`.
5. If validation is clean, run `002_indexes.sql`.
6. If duplicate and missing-reference checks are clean, run `003_constraints.sql`.
7. Switch `.env` to `DB_BACKEND=postgres`.

## Notes

- Do not commit CSV, dump, or backup files.
- Keep Access physical table and column names during the first migration.
- Add FK constraints only after confirming existing data has no missing references.

## 2026-05-26 Run

- `scripts/migrate_access_to_postgres.py --dry-run`: success.
- `scripts/migrate_access_to_postgres.py --apply-schema --truncate`: success.
- Imported rows:
  - `t_PGマスタ`: 2,026
  - `t_担当者マスタ`: 29
  - `t_貸出`: 31,795
- Validation:
  - `t_PGマスタ.ケースNo IS NULL`: 7
  - `t_貸出.返却日 IS NULL`: 419
  - `t_貸出.完了フラグ IS NULL`: 377
  - duplicate `サイズ`: 0
  - duplicate `担当者ID`: 0
  - duplicate `ID`: 0
  - missing `t_PGマスタ` reference from `t_貸出.サイズ`: 9,441
  - missing `t_担当者マスタ` reference from `t_貸出.担当者ID`: 0
- `002_indexes.sql`: applied.
- `003_constraints.sql`: not applied because FK to `t_PGマスタ` would fail.

## 2026-05-26 English Physical Names

- `004_rename_to_english.sql`: applied.
- PostgreSQL physical names are now:
  - `t_PGマスタ` -> `pg_master`
  - `t_担当者マスタ` -> `staff_master`
  - `t_貸出` -> `loans`
- Column names are now:
  - `pg_master`: `size`, `holding_count`, `case_no`
  - `staff_master`: `staff_id`, `staff_name`, `department`, `kana`, `visible`
  - `loans`: `id`, `size`, `staff_id`, `machine_code`, `lent_on`, `returned_on`, `completion_flag`
- Validation after rename:
  - `pg_master`: 2,026
  - `staff_master`: 29
  - `loans`: 31,795
  - missing `pg_master` reference from `loans.size`: 9,441
  - missing `staff_master` reference from `loans.staff_id`: 0
- PostgreSQL repository smoke check: passed.
- `003_constraints.sql`: still not applied because FK to `pg_master` would fail.

## Size Reconciliation Policy

Historical `loans.size` values include both pin-gauge sizes and special gauge labels.

Resolution:

1. Numeric loan sizes are normalized to the 3-decimal `pg_master.size` format when an existing master row matches.
   - Example: `1.03` -> `1.030`
2. Remaining historical sizes are inserted into `pg_master` as placeholder master rows.
   - `holding_count`: `0`
   - `case_no`: `NULL`
3. This keeps all loan history and allows `loans.size` -> `pg_master.size` FK enforcement.

## 2026-05-26 Size Reconciliation Run

- `005_reconcile_loan_sizes.sql`: applied.
- `pg_master`: 2,328
- `staff_master`: 29
- `loans`: 31,795
- missing `pg_master` reference from `loans.size`: 0
- missing `staff_master` reference from `loans.staff_id`: 0
- `003_constraints.sql`: applied.
- Repository smoke check after constraints: passed.

## 2026-06-09 Latest Access Refresh

- Source: current `\\192.168.1.200\共有\製造課\ピンゲージ管理.accdb`
- `scripts/migrate_access_to_postgres.py --dry-run`: success.
  - `pg_master`: 2,029 rows before reconciliation
  - `staff_master`: 29 rows
  - `loans`: 32,116 rows
  - `pg_master` placeholders added: 303
- `scripts/migrate_access_to_postgres.py --apply-schema --truncate`: success.
- `002_indexes.sql`: applied.
- Constraints: already present.
- Validation:
  - `pg_master`: 2,332
  - `staff_master`: 29
  - `loans`: 32,116
  - `pg_master.case_no IS NULL`: 310
  - `loans.returned_on IS NULL`: 452
  - `loans.completion_flag IS NULL`: 379
  - duplicate `pg_master.size`: 0
  - duplicate `staff_master.staff_id`: 0
  - duplicate `loans.id`: 0
  - missing `pg_master` reference from `loans.size`: 0
  - missing `staff_master` reference from `loans.staff_id`: 0
  - active loans: 379
  - returnable loans: 362
  - confirmation waiting: 17
