# PostgreSQL Migration Notes

## Current Target

- Host: `192.168.1.120`
- Database: `pingauge_management_db`
- Schema: `public`
- Source Access DB: `\\192.168.1.200\共有\生産管理課\AccessDB\ピンゲージ管理DB.accdb`

## Current Physical Names

| Access | PostgreSQL |
|---|---|
| `t_PGマスタ` | `pin_gauge_master` |
| `t_担当者マスタ` | `staff_master` |
| `t_貸出` | `pin_gauge_lending` |

| PostgreSQL table | Columns |
|---|---|
| `pin_gauge_master` | `size`, `owned_quantity`, `case_no` |
| `staff_master` | `staff_id`, `staff_name`, `department`, `kana`, `display_flag` |
| `pin_gauge_lending` | `id`, `size`, `staff_id`, `machine_no`, `lent_date`, `returned_date`, `completion_flag` |

Access query behavior is handled in Python repositories. PostgreSQL views are not used as substitutes for Access queries.

## Run Order

1. Create database `pingauge_management_db` in TablePlus or psql.
2. Run `001_schema.sql`.
3. Import data using `scripts/migrate_access_to_postgres.py` or `010_import_from_csv.sql`.
4. Run `020_validation.sql`.
5. If validation is clean, run `002_indexes.sql`.
6. If duplicate and missing-reference checks are clean, run `003_constraints.sql`.
7. Switch `.env` to `DB_BACKEND=postgres`.

## Notes

- Do not commit CSV, dump, or backup files.
- Keep Access physical table and column names during extraction.
- Add FK constraints only after confirming existing data has no missing references.
- `DATABASE_URL` is accepted for compatibility with the dedicated migration files under `docs/pingauge_management_db`.

## Size Reconciliation Policy

Historical `pin_gauge_lending.size` values may include both pin-gauge sizes and special gauge labels.

Resolution:

1. Numeric loan sizes are normalized to the 3-decimal `pin_gauge_master.size` format when an existing master row matches.
   - Example: `1.03` -> `1.030`
2. Remaining historical sizes are inserted into `pin_gauge_master` as placeholder master rows.
   - `owned_quantity`: `0`
   - `case_no`: `NULL`
3. This keeps all loan history and allows `pin_gauge_lending.size` -> `pin_gauge_master.size` FK enforcement.

## 2026-06-15 ピンゲージ管理DB Refresh

- Source: `\\192.168.1.200\共有\生産管理課\AccessDB\ピンゲージ管理DB.accdb`
- Dedicated reference folder: `docs/pingauge_management_db`
- Target database: `pingauge_management_db`
- Verified table and column existence through PostgreSQL connection.
- Verified application repository reads:
  - `pin_gauge_master`: 2,030 rows
  - `staff_master`: 29 rows
  - `pin_gauge_lending`: 32,229 rows
  - active confirmation/search repository read: passed
- Validation sample:
  - active loans from app repository: 411
- UI behavior update:
  - Confirmation batches refresh automatically when opening the confirmation screen.
  - Confirmation batches refresh automatically after single/bulk return operations.

## Dedicated Migration Result

`docs/pingauge_management_db/migration_result_pingauge_management_db.md` recorded:

| Access table | PostgreSQL table | Access rows | PostgreSQL rows | Status |
|---|---|---:|---:|---|
| `t_PGマスタ` | `pin_gauge_master` | 2,030 | 2,030 | Success |
| `t_担当者マスタ` | `staff_master` | 29 | 29 | Success |
| `t_貸出` | `pin_gauge_lending` | 32,229 | 32,229 | Success |
