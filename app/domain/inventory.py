from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Inventory:
    size: str
    holding_count: int
    case_no: str

