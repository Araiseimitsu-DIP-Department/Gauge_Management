-- CSV import template.
-- Adjust absolute paths before running, or import via TablePlus with the same column order.

TRUNCATE TABLE "loans", "pg_master", "staff_master" RESTART IDENTITY;

COPY "pg_master" ("size", "holding_count", "case_no")
FROM 'C:/Users/SEIZOU20/PythonProjects/Gauge_Management/database/postgresql/export/t_PGマスタ.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8', NULL '');

COPY "staff_master" ("staff_id", "staff_name", "department", "kana", "visible")
FROM 'C:/Users/SEIZOU20/PythonProjects/Gauge_Management/database/postgresql/export/t_担当者マスタ.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8', NULL '');

COPY "loans" ("id", "size", "staff_id", "machine_code", "lent_on", "returned_on", "completion_flag")
FROM 'C:/Users/SEIZOU20/PythonProjects/Gauge_Management/database/postgresql/export/t_貸出.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8', NULL '');

SELECT setval(
  pg_get_serial_sequence('public."loans"', 'id'),
  COALESCE((SELECT MAX("id") FROM "loans"), 1),
  true
);
