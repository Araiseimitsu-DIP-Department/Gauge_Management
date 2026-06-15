-- CSV import template.
-- Adjust absolute paths before running, or import via TablePlus with the same column order.

TRUNCATE TABLE "pin_gauge_lending", "pin_gauge_master", "staff_master" RESTART IDENTITY;

COPY "pin_gauge_master" ("size", "owned_quantity", "case_no")
FROM 'C:/Users/SEIZOU20/PythonProjects/Gauge_Management/database/postgresql/export/t_PGマスタ.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8', NULL '');

COPY "staff_master" ("staff_id", "staff_name", "department", "kana", "display_flag")
FROM 'C:/Users/SEIZOU20/PythonProjects/Gauge_Management/database/postgresql/export/t_担当者マスタ.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8', NULL '');

COPY "pin_gauge_lending" ("id", "size", "staff_id", "machine_no", "lent_date", "returned_date", "completion_flag")
FROM 'C:/Users/SEIZOU20/PythonProjects/Gauge_Management/database/postgresql/export/t_貸出.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8', NULL '');

SELECT setval(
  pg_get_serial_sequence('public."pin_gauge_lending"', 'id'),
  COALESCE((SELECT MAX("id") FROM "pin_gauge_lending"), 1),
  true
);
