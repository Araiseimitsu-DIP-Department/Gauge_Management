-- Reconcile loan sizes before applying FK constraints.
--
-- 1. Normalize numeric loan sizes to the 3-decimal format used by pg_master
--    when that normalized value already exists in pg_master.
-- 2. Add placeholder pg_master rows for remaining historical loan sizes
--    such as special gauges and non-pin-gauge labels.

UPDATE "loans" AS l
SET "size" = to_char(l."size"::numeric, 'FM999999990.000')
WHERE l."size" ~ '^[0-9]+(\.[0-9]+)?$'
  AND NOT EXISTS (
    SELECT 1
    FROM "pg_master" AS exact
    WHERE exact."size" = l."size"
  )
  AND EXISTS (
    SELECT 1
    FROM "pg_master" AS formatted
    WHERE formatted."size" = to_char(l."size"::numeric, 'FM999999990.000')
  );

INSERT INTO "pg_master" ("size", "holding_count", "case_no")
SELECT DISTINCT l."size", 0, NULL
FROM "loans" AS l
LEFT JOIN "pg_master" AS m ON l."size" = m."size"
WHERE m."size" IS NULL
ORDER BY l."size";
