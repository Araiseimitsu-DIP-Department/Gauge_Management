-- Rename existing Japanese PostgreSQL physical names to the current English names.
-- Run this once against a database already migrated with the Japanese schema.

ALTER TABLE IF EXISTS "t_PGマスタ" RENAME TO "pin_gauge_master";
ALTER TABLE IF EXISTS "t_担当者マスタ" RENAME TO "staff_master";
ALTER TABLE IF EXISTS "t_貸出" RENAME TO "pin_gauge_lending";

ALTER TABLE "pin_gauge_master" RENAME COLUMN "サイズ" TO "size";
ALTER TABLE "pin_gauge_master" RENAME COLUMN "保有数" TO "owned_quantity";
ALTER TABLE "pin_gauge_master" RENAME COLUMN "ケースNo" TO "case_no";

ALTER TABLE "staff_master" RENAME COLUMN "担当者ID" TO "staff_id";
ALTER TABLE "staff_master" RENAME COLUMN "担当者名" TO "staff_name";
ALTER TABLE "staff_master" RENAME COLUMN "部署" TO "department";
ALTER TABLE "staff_master" RENAME COLUMN "かな" TO "kana";
ALTER TABLE "staff_master" RENAME COLUMN "表示" TO "display_flag";

ALTER TABLE "pin_gauge_lending" RENAME COLUMN "ID" TO "id";
ALTER TABLE "pin_gauge_lending" RENAME COLUMN "サイズ" TO "size";
ALTER TABLE "pin_gauge_lending" RENAME COLUMN "担当者ID" TO "staff_id";
ALTER TABLE "pin_gauge_lending" RENAME COLUMN "機番" TO "machine_no";
ALTER TABLE "pin_gauge_lending" RENAME COLUMN "貸出日" TO "lent_date";
ALTER TABLE "pin_gauge_lending" RENAME COLUMN "返却日" TO "returned_date";
ALTER TABLE "pin_gauge_lending" RENAME COLUMN "完了フラグ" TO "completion_flag";

ALTER INDEX IF EXISTS "ix_t_PGマスタ_ケースNo" RENAME TO "ix_pin_gauge_master_case_no";
ALTER INDEX IF EXISTS "ix_t_担当者マスタ_表示_部署_かな" RENAME TO "ix_staff_master_display_department_kana";
ALTER INDEX IF EXISTS "ix_t_貸出_サイズ" RENAME TO "ix_pin_gauge_lending_size";
ALTER INDEX IF EXISTS "ix_t_貸出_機番_未返却" RENAME TO "ix_pin_gauge_lending_machine_no_returnable";
ALTER INDEX IF EXISTS "ix_t_貸出_返却日_完了フラグ" RENAME TO "ix_pin_gauge_lending_returned_completion";
ALTER INDEX IF EXISTS "ix_t_貸出_貸出日_機番_担当者ID" RENAME TO "ix_pin_gauge_lending_lent_machine_staff";
