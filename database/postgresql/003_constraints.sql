-- Constraints to add after importing and validating Access data.

ALTER TABLE "pin_gauge_master"
  ADD CONSTRAINT "pk_pin_gauge_master" PRIMARY KEY ("size"),
  ADD CONSTRAINT "ck_pin_gauge_master_owned_quantity" CHECK ("owned_quantity" IS NULL OR "owned_quantity" >= 0);

ALTER TABLE "staff_master"
  ADD CONSTRAINT "pk_staff_master" PRIMARY KEY ("staff_id"),
  ADD CONSTRAINT "ck_staff_master_display_flag" CHECK ("display_flag" IS NULL OR "display_flag" IN ('Y', 'N'));

ALTER TABLE "pin_gauge_lending"
  ADD CONSTRAINT "pk_pin_gauge_lending" PRIMARY KEY ("id"),
  ADD CONSTRAINT "ck_pin_gauge_lending_completion_flag" CHECK ("completion_flag" IS NULL OR "completion_flag" IN ('Y', 'N'));

ALTER TABLE "pin_gauge_lending"
  ADD CONSTRAINT "fk_pin_gauge_lending_staff"
  FOREIGN KEY ("staff_id")
  REFERENCES "staff_master" ("staff_id");

ALTER TABLE "pin_gauge_lending"
  ADD CONSTRAINT "fk_pin_gauge_lending_master"
  FOREIGN KEY ("size")
  REFERENCES "pin_gauge_master" ("size");
