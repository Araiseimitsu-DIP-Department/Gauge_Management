-- Validation SQL for the first Access -> PostgreSQL migration.

-- Row counts. Expected:
-- pg_master: 2328 after size reconciliation
-- staff_master: 29
-- loans: 31753+
SELECT 'pg_master' AS table_name, COUNT(*) AS row_count FROM "pg_master"
UNION ALL
SELECT 'staff_master', COUNT(*) FROM "staff_master"
UNION ALL
SELECT 'loans', COUNT(*) FROM "loans";

-- NULL counts. Expected from docs/ピンゲージ管理_meta.md:
-- pg_master.case_no IS NULL: 309 after placeholder rows are added
-- loans.returned_on IS NULL: 405+
-- loans.completion_flag IS NULL: 338+
SELECT
  COUNT(*) FILTER (WHERE "case_no" IS NULL) AS null_case_no
FROM "pg_master";

SELECT
  COUNT(*) FILTER (WHERE "returned_on" IS NULL) AS null_returned_on,
  COUNT(*) FILTER (WHERE "completion_flag" IS NULL) AS null_completion_flag
FROM "loans";

-- Duplicate primary key candidates. All should return zero rows.
SELECT "size", COUNT(*)
FROM "pg_master"
GROUP BY "size"
HAVING COUNT(*) > 1;

SELECT "staff_id", COUNT(*)
FROM "staff_master"
GROUP BY "staff_id"
HAVING COUNT(*) > 1;

SELECT "id", COUNT(*)
FROM "loans"
GROUP BY "id"
HAVING COUNT(*) > 1;

-- Missing foreign key candidates. Both counts should be 0 before adding FK constraints.
SELECT COUNT(*) AS missing_pg_master
FROM "loans" l
LEFT JOIN "pg_master" m ON l."size" = m."size"
WHERE m."size" IS NULL;

SELECT COUNT(*) AS missing_staff
FROM "loans" l
LEFT JOIN "staff_master" s ON l."staff_id" = s."staff_id"
WHERE s."staff_id" IS NULL;

-- Application smoke-test queries.
SELECT COUNT(*) AS active_loans
FROM "loans"
WHERE "completion_flag" IS NULL;

SELECT COUNT(*) AS returnable_loans
FROM "loans"
WHERE "returned_on" IS NULL AND "completion_flag" IS NULL;

SELECT COUNT(*) AS confirmation_waiting
FROM "loans"
WHERE "completion_flag" = 'N'
   OR ("completion_flag" IS NULL AND "returned_on" IS NOT NULL);
