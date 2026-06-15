-- Validation SQL for the first Access -> PostgreSQL migration.

-- Row counts. Expected:
-- pin_gauge_master: 2030
-- staff_master: 29
-- pin_gauge_lending: 32229
SELECT 'pin_gauge_master' AS table_name, COUNT(*) AS row_count FROM "pin_gauge_master"
UNION ALL
SELECT 'staff_master', COUNT(*) FROM "staff_master"
UNION ALL
SELECT 'pin_gauge_lending', COUNT(*) FROM "pin_gauge_lending";

-- NULL counts.
SELECT
  COUNT(*) FILTER (WHERE "case_no" IS NULL) AS null_case_no
FROM "pin_gauge_master";

SELECT
  COUNT(*) FILTER (WHERE "returned_date" IS NULL) AS null_returned_date,
  COUNT(*) FILTER (WHERE "completion_flag" IS NULL) AS null_completion_flag
FROM "pin_gauge_lending";

-- Duplicate primary key candidates. All should return zero rows.
SELECT "size", COUNT(*)
FROM "pin_gauge_master"
GROUP BY "size"
HAVING COUNT(*) > 1;

SELECT "staff_id", COUNT(*)
FROM "staff_master"
GROUP BY "staff_id"
HAVING COUNT(*) > 1;

SELECT "id", COUNT(*)
FROM "pin_gauge_lending"
GROUP BY "id"
HAVING COUNT(*) > 1;

-- Missing foreign key candidates. Both counts should be 0 before adding FK constraints.
SELECT COUNT(*) AS missing_pin_gauge_master
FROM "pin_gauge_lending" l
LEFT JOIN "pin_gauge_master" m ON l."size" = m."size"
WHERE m."size" IS NULL;

SELECT COUNT(*) AS missing_staff
FROM "pin_gauge_lending" l
LEFT JOIN "staff_master" s ON l."staff_id" = s."staff_id"
WHERE s."staff_id" IS NULL;

-- Application smoke-test queries.
SELECT COUNT(*) AS active_loans
FROM "pin_gauge_lending"
WHERE "completion_flag" IS NULL;

SELECT COUNT(*) AS returnable_loans
FROM "pin_gauge_lending"
WHERE "returned_date" IS NULL AND "completion_flag" IS NULL;

SELECT COUNT(*) AS confirmation_waiting
FROM "pin_gauge_lending"
WHERE "completion_flag" = 'N'
   OR ("completion_flag" IS NULL AND "returned_date" IS NOT NULL);
