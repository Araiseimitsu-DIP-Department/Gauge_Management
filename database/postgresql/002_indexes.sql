-- Indexes based on the current application search patterns.

CREATE INDEX IF NOT EXISTS "ix_pg_master_case_no"
  ON "pg_master" ("case_no");

CREATE INDEX IF NOT EXISTS "ix_staff_master_visible_department_kana"
  ON "staff_master" ("visible", "department", "kana");

CREATE INDEX IF NOT EXISTS "ix_loans_size"
  ON "loans" ("size");

CREATE INDEX IF NOT EXISTS "ix_loans_machine_code_returnable"
  ON "loans" ("machine_code")
  WHERE "returned_on" IS NULL AND "completion_flag" IS NULL;

CREATE INDEX IF NOT EXISTS "ix_loans_returned_on_completion_flag"
  ON "loans" ("returned_on", "completion_flag");

CREATE INDEX IF NOT EXISTS "ix_loans_lent_on_machine_code_staff_id"
  ON "loans" ("lent_on", "machine_code", "staff_id");
