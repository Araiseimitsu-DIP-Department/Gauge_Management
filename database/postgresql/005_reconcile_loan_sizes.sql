-- Reconcile loan sizes before applying FK constraints.
--
-- 1. Normalize numeric loan sizes to the 3-decimal format used by pin_gauge_master
--    when that normalized value already exists in pin_gauge_master.
-- 2. Add placeholder pin_gauge_master rows for remaining historical loan sizes
--    such as special gauges and non-pin-gauge labels.

UPDATE "pin_gauge_lending" AS l
SET "size" = to_char(l."size"::numeric, 'FM999999990.000')
WHERE l."size" ~ '^[0-9]+(\.[0-9]+)?$'
  AND NOT EXISTS (
    SELECT 1
    FROM "pin_gauge_master" AS exact
    WHERE exact."size" = l."size"
  )
  AND EXISTS (
    SELECT 1
    FROM "pin_gauge_master" AS formatted
    WHERE formatted."size" = to_char(l."size"::numeric, 'FM999999990.000')
  );

INSERT INTO "pin_gauge_master" ("size", "owned_quantity", "case_no")
SELECT DISTINCT l."size", 0, NULL
FROM "pin_gauge_lending" AS l
LEFT JOIN "pin_gauge_master" AS m ON l."size" = m."size"
WHERE m."size" IS NULL
ORDER BY l."size";
