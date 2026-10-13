-- CSV import template.
-- Adjust absolute paths before running, or import via TablePlus with the same column order.

BEGIN;
SET LOCAL lock_timeout = '5s';

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

-- ID明示投入後の補正は登録・採番をロックし、採番値を後戻りさせない。
LOCK TABLE "pin_gauge_lending" IN SHARE ROW EXCLUSIVE MODE;
DO $sequence_sync$
DECLARE
  sequence_name regclass := pg_get_serial_sequence('"pin_gauge_lending"', 'id');
  maximum_id bigint;
  current_value bigint;
  called boolean;
  increment_value bigint;
  cache_size bigint;
  limit_value bigint;
  cycles boolean;
BEGIN
  IF sequence_name IS NULL THEN
    RAISE EXCEPTION '貸出IDのシーケンスがありません';
  END IF;
  SELECT seqincrement, seqcache, seqmax, seqcycle
  INTO increment_value, cache_size, limit_value, cycles
  FROM pg_sequence WHERE seqrelid = sequence_name;
  IF increment_value <> 1 OR cycles THEN
    RAISE EXCEPTION '増分1・循環なし以外の採番は補正しません';
  END IF;
  EXECUTE format('ALTER SEQUENCE %s CACHE %s', sequence_name, cache_size);
  EXECUTE format('SELECT last_value, is_called FROM %s', sequence_name) INTO current_value, called;
  SELECT MAX(id) INTO maximum_id FROM "pin_gauge_lending";
  IF maximum_id IS NOT NULL AND (current_value < maximum_id OR (current_value = maximum_id AND NOT called)) THEN
    IF maximum_id >= limit_value THEN
      RAISE EXCEPTION '貸出IDが採番上限に達しています';
    END IF;
    EXECUTE format('ALTER SEQUENCE %s RESTART WITH %s', sequence_name, maximum_id + 1);
  END IF;
END
$sequence_sync$;
COMMIT;
