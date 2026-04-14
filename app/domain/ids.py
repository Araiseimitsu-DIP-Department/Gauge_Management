from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoanId:
    value: int


@dataclass(frozen=True)
class StaffId:
    value: str


@dataclass(frozen=True)
class InventoryId:
    value: str

