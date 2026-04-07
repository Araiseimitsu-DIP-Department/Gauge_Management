from __future__ import annotations

from datetime import date

from app.utils.errors import AppValidationError


NUMBER_MACHINE_PREFIX = "数値"


def build_machine_code(prefix: str, suffix: str) -> str | None:
    normalized_prefix = prefix.strip()
    normalized_suffix = suffix.strip()

    if not normalized_prefix:
        return None

    if normalized_prefix == NUMBER_MACHINE_PREFIX:
        return NUMBER_MACHINE_PREFIX

    if not normalized_suffix:
        return None

    return f"{normalized_prefix}-{normalized_suffix}"


def normalize_gauge_sizes(values: list[str]) -> list[str]:
    normalized_values: list[str] = []

    for value in values:
        normalized = value.strip().upper()
        if normalized:
            normalized_values.append(normalized)

    return normalized_values


def validate_lending_registration(
    *,
    lent_on: date | None,
    machine_prefix: str,
    machine_suffix: str,
    staff_id: str | None,
    gauge_sizes: list[str],
) -> tuple[str, list[str]]:
    if lent_on is None:
        raise AppValidationError("貸出日を入力してください。")

    machine_code = build_machine_code(machine_prefix, machine_suffix)
    if not machine_code:
        raise AppValidationError("機番を入力してください。")

    if not staff_id:
        raise AppValidationError("担当者を選択してください。")

    normalized_sizes = normalize_gauge_sizes(gauge_sizes)
    if not normalized_sizes:
        raise AppValidationError("少なくとも1件のサイズを入力してください。")

    return machine_code, normalized_sizes


def validate_lending_search(
    *,
    search_mode: str,
    size_prefix: str,
    machine_prefix: str,
    machine_suffix: str,
) -> tuple[str | None, str | None]:
    normalized_size_prefix = size_prefix.strip().upper() or None
    machine_code = build_machine_code(machine_prefix, machine_suffix)

    if search_mode == "size":
        if not normalized_size_prefix:
            raise AppValidationError("サイズ検索を選んだ場合はサイズを入力してください。")
        return normalized_size_prefix, None

    if search_mode == "machine":
        if not machine_code:
            raise AppValidationError("機番検索を選んだ場合は機番を入力してください。")
        return None, machine_code

    if normalized_size_prefix:
        return normalized_size_prefix, None

    return None, machine_code


def validate_return_case_no(case_no: str) -> str:
    normalized = case_no.strip().upper()
    if not normalized:
        raise AppValidationError("返却ケースNoを入力してください。")
    if len(normalized) > 2:
        raise AppValidationError("返却ケースNoは2桁以内にしてください。")
    return normalized


def validate_pg_master_record(size: str, holding_count: int | None, case_no: str) -> tuple[str, int, str]:
    normalized_size = size.strip().upper()
    normalized_case_no = case_no.strip().upper()

    if not normalized_size or holding_count is None or not normalized_case_no:
        raise AppValidationError("サイズ・保有数・ケースNoは必ず入力してください。")

    return normalized_size, int(holding_count), normalized_case_no
