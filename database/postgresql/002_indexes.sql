-- Indexes based on the current application search patterns.

CREATE INDEX IF NOT EXISTS "ix_pin_gauge_master_case_no"
  ON "pin_gauge_master" ("case_no");

CREATE INDEX IF NOT EXISTS "ix_staff_master_display_department_kana"
  ON "staff_master" ("display_flag", "department", "kana");

CREATE INDEX IF NOT EXISTS "ix_pin_gauge_lending_size"
  ON "pin_gauge_lending" ("size");

CREATE INDEX IF NOT EXISTS "ix_pin_gauge_lending_machine_no_returnable"
  ON "pin_gauge_lending" ("machine_no")
  WHERE "returned_date" IS NULL AND "completion_flag" IS NULL;

CREATE INDEX IF NOT EXISTS "ix_pin_gauge_lending_returned_completion"
  ON "pin_gauge_lending" ("returned_date", "completion_flag");

CREATE INDEX IF NOT EXISTS "ix_pin_gauge_lending_lent_machine_staff"
  ON "pin_gauge_lending" ("lent_date", "machine_no", "staff_id");
