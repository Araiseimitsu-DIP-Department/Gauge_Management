from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PgMasterRecord:
    size: str
    holding_count: int
    case_no: str
