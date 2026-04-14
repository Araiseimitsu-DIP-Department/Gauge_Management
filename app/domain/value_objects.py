from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MachineCode:
    value: str


@dataclass(frozen=True)
class CaseNo:
    value: str


@dataclass(frozen=True)
class CompletionFlag:
    value: bool


@dataclass(frozen=True)
class BusinessDate:
    value: date

