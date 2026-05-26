-- Constraints to add after importing and validating Access data.

ALTER TABLE "pg_master"
  ADD CONSTRAINT "pk_pg_master" PRIMARY KEY ("size"),
  ADD CONSTRAINT "ck_pg_master_holding_count" CHECK ("holding_count" >= 0);

ALTER TABLE "staff_master"
  ADD CONSTRAINT "pk_staff_master" PRIMARY KEY ("staff_id"),
  ADD CONSTRAINT "ck_staff_master_visible" CHECK ("visible" IN ('Y', 'N'));

ALTER TABLE "loans"
  ADD CONSTRAINT "pk_loans" PRIMARY KEY ("id"),
  ADD CONSTRAINT "ck_loans_completion_flag" CHECK ("completion_flag" IS NULL OR "completion_flag" IN ('Y', 'N'));

ALTER TABLE "loans"
  ADD CONSTRAINT "fk_loans_staff"
  FOREIGN KEY ("staff_id")
  REFERENCES "staff_master" ("staff_id");

ALTER TABLE "loans"
  ADD CONSTRAINT "fk_loans_pg_master"
  FOREIGN KEY ("size")
  REFERENCES "pg_master" ("size");
