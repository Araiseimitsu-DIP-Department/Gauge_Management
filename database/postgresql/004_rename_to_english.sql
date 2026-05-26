-- Rename existing Japanese PostgreSQL physical names to English names.
-- Run this once against a database already migrated with the Japanese schema.

ALTER TABLE IF EXISTS "t_PGマスタ" RENAME TO "pg_master";
ALTER TABLE IF EXISTS "t_担当者マスタ" RENAME TO "staff_master";
ALTER TABLE IF EXISTS "t_貸出" RENAME TO "loans";

ALTER TABLE "pg_master" RENAME COLUMN "サイズ" TO "size";
ALTER TABLE "pg_master" RENAME COLUMN "保有数" TO "holding_count";
ALTER TABLE "pg_master" RENAME COLUMN "ケースNo" TO "case_no";

ALTER TABLE "staff_master" RENAME COLUMN "担当者ID" TO "staff_id";
ALTER TABLE "staff_master" RENAME COLUMN "担当者名" TO "staff_name";
ALTER TABLE "staff_master" RENAME COLUMN "部署" TO "department";
ALTER TABLE "staff_master" RENAME COLUMN "かな" TO "kana";
ALTER TABLE "staff_master" RENAME COLUMN "表示" TO "visible";

ALTER TABLE "loans" RENAME COLUMN "ID" TO "id";
ALTER TABLE "loans" RENAME COLUMN "サイズ" TO "size";
ALTER TABLE "loans" RENAME COLUMN "担当者ID" TO "staff_id";
ALTER TABLE "loans" RENAME COLUMN "機番" TO "machine_code";
ALTER TABLE "loans" RENAME COLUMN "貸出日" TO "lent_on";
ALTER TABLE "loans" RENAME COLUMN "返却日" TO "returned_on";
ALTER TABLE "loans" RENAME COLUMN "完了フラグ" TO "completion_flag";

ALTER INDEX IF EXISTS "ix_t_PGマスタ_ケースNo" RENAME TO "ix_pg_master_case_no";
ALTER INDEX IF EXISTS "ix_t_担当者マスタ_表示_部署_かな" RENAME TO "ix_staff_master_visible_department_kana";
ALTER INDEX IF EXISTS "ix_t_貸出_サイズ" RENAME TO "ix_loans_size";
ALTER INDEX IF EXISTS "ix_t_貸出_機番_未返却" RENAME TO "ix_loans_machine_code_returnable";
ALTER INDEX IF EXISTS "ix_t_貸出_返却日_完了フラグ" RENAME TO "ix_loans_returned_on_completion_flag";
ALTER INDEX IF EXISTS "ix_t_貸出_貸出日_機番_担当者ID" RENAME TO "ix_loans_lent_on_machine_code_staff_id";
