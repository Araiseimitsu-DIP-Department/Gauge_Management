from __future__ import annotations

from dataclasses import dataclass
from typing import Any

LENDING_TABLE = "pin_gauge_lending"
ID_COLUMN = "id"
LOCK_TIMEOUT = "5s"


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


@dataclass(frozen=True)
class LoanSequenceState:
    sequence_schema: str
    sequence_name: str
    maximum_id: int | None
    last_value: int
    is_called: bool
    increment: int
    cache_size: int
    maximum_value: int
    cycle: bool

    @property
    def next_id(self) -> int:
        return self.last_value + self.increment if self.is_called else self.last_value

    @property
    def needs_repair(self) -> bool:
        return self.maximum_id is not None and self.next_id <= self.maximum_id

    @property
    def qualified_sequence(self) -> str:
        return f"{quote_identifier(self.sequence_schema)}.{quote_identifier(self.sequence_name)}"


def read_loan_sequence(cursor: Any, schema: str) -> LoanSequenceState:
    table = f"{quote_identifier(schema)}.{quote_identifier(LENDING_TABLE)}"
    cursor.execute("SELECT pg_get_serial_sequence(%s, %s)", (table, ID_COLUMN))
    sequence = cursor.fetchone()[0]
    if sequence is None:
        raise ValueError("貸出IDに関連付けられたシーケンスがありません。DB定義を確認してください。")
    cursor.execute(
        "SELECT n.nspname, c.relname, s.seqincrement, s.seqcache, s.seqmax, s.seqcycle "
        "FROM pg_sequence s JOIN pg_class c ON c.oid=s.seqrelid "
        "JOIN pg_namespace n ON n.oid=c.relnamespace WHERE s.seqrelid=%s::regclass",
        (sequence,),
    )
    sequence_schema, sequence_name, increment, cache_size, maximum_value, cycle = cursor.fetchone()
    qualified_sequence = f"{quote_identifier(sequence_schema)}.{quote_identifier(sequence_name)}"
    cursor.execute(f"SELECT last_value, is_called FROM {qualified_sequence}")
    last_value, is_called = cursor.fetchone()
    cursor.execute(f"SELECT MAX({quote_identifier(ID_COLUMN)}) FROM {table}")
    return LoanSequenceState(
        sequence_schema, sequence_name, cursor.fetchone()[0],
        last_value, is_called, increment, cache_size, maximum_value, cycle,
    )


def synchronize_loan_sequence(cursor: Any, schema: str) -> tuple[LoanSequenceState, LoanSequenceState]:
    """行を変更せず、登録と採番をロックして不足した採番値だけを進める。commitは呼出元で行う。"""
    table = f"{quote_identifier(schema)}.{quote_identifier(LENDING_TABLE)}"
    cursor.execute("SELECT set_config('lock_timeout', %s, true)", (LOCK_TIMEOUT,))
    cursor.execute(f"LOCK TABLE {table} IN SHARE ROW EXCLUSIVE MODE")
    before = read_loan_sequence(cursor, schema)
    if before.increment != 1 or before.cycle:
        raise ValueError("増分1・循環なし以外のシーケンスは自動補正しません。")
    # 同じキャッシュ値を指定してシーケンスのDDLロックを取得し、直接のnextvalも止める。
    cursor.execute(f"ALTER SEQUENCE {before.qualified_sequence} CACHE {before.cache_size}")
    locked = read_loan_sequence(cursor, schema)
    if locked.needs_repair:
        next_id = locked.maximum_id + locked.increment
        if next_id > locked.maximum_value:
            raise ValueError("採番上限を超えるため補正できません。")
        # RESTARTはトランザクション内で実施し、失敗時にロールバックできる。
        cursor.execute(f"ALTER SEQUENCE {locked.qualified_sequence} RESTART WITH {next_id}")
    after = read_loan_sequence(cursor, schema)
    if after.needs_repair or after.next_id < locked.next_id:
        raise RuntimeError("採番補正後の整合確認に失敗しました。")
    return locked, after
