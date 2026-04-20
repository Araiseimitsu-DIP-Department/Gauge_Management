from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from typing import Any

from app.config.app_settings import AppSettings
from app.services.lending_service import LendingService
from app.services.master_service import MasterService
from app.services.operation_service import OperationService
from app.utils.errors import AppConfigurationError, AppDataAccessError, AppValidationError
from app.utils.validators import NUMBER_MACHINE_PREFIX


class WebviewBridge:
    def __init__(
        self,
        *,
        settings: AppSettings,
        lending_service: LendingService,
        operation_service: OperationService,
        master_service: MasterService,
    ) -> None:
        self._settings = settings
        self._lending_service = lending_service
        self._operation_service = operation_service
        self._master_service = master_service

    def bootstrap(self) -> dict[str, Any]:
        errors: list[str] = []

        try:
            self._master_service.normalize_staff_departments()
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            errors.append(str(exc))

        def load(loader) -> list[dict[str, Any]]:
            try:
                return self._serialize_rows(loader())
            except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
                errors.append(str(exc))
                return []

        today = date.today().isoformat()
        state = {
            "app_name": self._settings.app_name,
            "environment": self._settings.environment,
            "database_backend": self._settings.database_backend,
            "current_date": today,
            "screen_titles": {
                "lending": {"title": "貸出", "subtitle": "貸出登録と貸出一覧"},
                "return": {"title": "返却", "subtitle": "返却対象の検索と返却処理"},
                "confirmation": {"title": "確認", "subtitle": "返却済みデータの確認処理"},
                "pg_master": {"title": "PGマスタ", "subtitle": "PGマスタの検索と編集"},
                "staff_master": {"title": "担当者マスタ", "subtitle": "担当者情報の編集"},
            },
            "options": {
                "lending_machine_prefixes": ["", "A", "B", "C", "D", "E", "F", NUMBER_MACHINE_PREFIX, "返"],
                "return_machine_prefixes": ["", "A", "B", "C", "D", "E", "F", NUMBER_MACHINE_PREFIX],
                "machine_suffixes": [""] + [str(index) for index in range(1, 17)],
                "departments": ["製造", "数値", "その他"],
            },
            "number_machine_prefix": NUMBER_MACHINE_PREFIX,
            "lending": {
                "register_date": today,
                "register_machine_prefix": "",
                "register_machine_suffix": "",
                "register_staff_id": "",
                "register_gauge_sizes": [""] * 20,
                "search_mode": "size",
                "search_size_prefix": "",
                "search_machine_prefix": "",
                "search_machine_suffix": "",
                "use_size_prefix_match": False,
                "staff_members": [],
                "loans": [],
                "selected_loan_id": None,
            },
            "return": {
                "date": today,
                "machine_prefix": "",
                "machine_suffix": "",
                "case_no": "",
                "loans": [],
                "selected_loan_id": None,
            },
            "confirmation": {
                "case_no": "",
                "detail_loans": [],
                "selected_loan_id": None,
                "batches": load(self._operation_service.fetch_confirmation_batches),
                "selected_batch_machine_code": "",
            },
            "pg_master": {
                "search_query": "",
                "rows": load(lambda: self._master_service.search_pg_master("")),
                "selected_size": "",
                "edit_size": "",
                "edit_holding_count": 0,
                "edit_case_no": "",
                "is_new": True,
            },
            "staff_master": {
                "search_query": "",
                "rows": load(lambda: self._master_service.search_staff_master("")),
                "selected_staff_id": "",
                "edit_staff_id": "",
                "edit_name": "",
                "edit_department": "製造",
                "edit_kana": "",
                "edit_visible": True,
            },
            "initial_errors": errors,
        }
        return self._ok(state)

    def get_staff_members(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            machine_prefix = str(payload.get("machine_prefix", "")).strip()
            staff_members = self._lending_service.load_staff_members(machine_prefix)
            return self._ok({"staff_members": self._serialize_rows(staff_members)})
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def search_lending(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            loans = self._lending_service.search_loans(
                search_mode=str(payload.get("search_mode", "size")),
                size_prefix=str(payload.get("size_prefix", "")),
                machine_prefix=str(payload.get("machine_prefix", "")),
                machine_suffix=str(payload.get("machine_suffix", "")),
                use_size_prefix_match=bool(payload.get("use_size_prefix_match", False)),
            )
            return self._ok({"loans": self._serialize_rows(loans)})
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def register_lending(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            loans = self._lending_service.register_loans(
                lent_on=self._parse_date(payload.get("lent_on")),
                machine_prefix=str(payload.get("machine_prefix", "")),
                machine_suffix=str(payload.get("machine_suffix", "")),
                staff_id=self._optional_text(payload.get("staff_id")),
                gauge_sizes=[str(value) for value in payload.get("gauge_sizes", [])],
            )
            return self._ok({"loans": self._serialize_rows(loans)})
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def update_loan(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            self._lending_service.update_loan(
                loan_id=int(payload["loan_id"]),
                lent_on=self._parse_date(payload.get("lent_on")),
                machine_code=str(payload.get("machine_code", "")),
                staff_id=self._optional_text(payload.get("staff_id")),
                size=str(payload.get("size", "")),
            )
            return self._ok({})
        except (KeyError, ValueError) as exc:
            return self._fail(AppValidationError(f"Invalid payload: {exc}"))
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def delete_loan(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            self._lending_service.delete_loan(int(payload["loan_id"]))
            return self._ok({})
        except (KeyError, ValueError) as exc:
            return self._fail(AppValidationError(f"Invalid payload: {exc}"))
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def search_returnable_loans(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            loans = self._operation_service.search_returnable_loans(
                str(payload.get("machine_prefix", "")),
                str(payload.get("machine_suffix", "")),
            )
            return self._ok({"loans": self._serialize_rows(loans)})
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def return_one_loan(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            self._operation_service.return_one_loan(
                loan_id=self._optional_int(payload.get("loan_id")),
                case_no=str(payload.get("case_no", "")),
                returned_on=self._parse_date(payload.get("returned_on")),
            )
            return self._ok({})
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def return_all_loans(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            count = self._operation_service.return_all_loans(
                machine_prefix=str(payload.get("machine_prefix", "")),
                machine_suffix=str(payload.get("machine_suffix", "")),
                case_no=str(payload.get("case_no", "")),
                returned_on=self._parse_date(payload.get("returned_on")),
                target_count=int(payload.get("target_count", 0)),
            )
            return self._ok({"count": count})
        except (AppConfigurationError, AppValidationError, AppDataAccessError, ValueError) as exc:
            return self._fail(exc)

    def search_confirmation_loans(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            loans = self._operation_service.search_confirmation_loans(str(payload.get("case_no", "")))
            return self._ok({"loans": self._serialize_rows(loans)})
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def fetch_confirmation_batches(self) -> dict[str, Any]:
        try:
            batches = self._operation_service.fetch_confirmation_batches()
            return self._ok({"batches": self._serialize_rows(batches)})
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def confirm_one(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            self._operation_service.confirm_one(self._optional_int(payload.get("loan_id")))
            return self._ok({})
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def confirm_all(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            loan_ids = [int(value) for value in payload.get("loan_ids", [])]
            count = self._operation_service.confirm_all(loan_ids)
            return self._ok({"count": count})
        except (TypeError, ValueError) as exc:
            return self._fail(AppValidationError(f"Invalid payload: {exc}"))
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def search_pg_master(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            rows = self._master_service.search_pg_master(str(payload.get("size_query", "")))
            return self._ok({"rows": self._serialize_rows(rows)})
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def save_pg_master(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            self._master_service.save_pg_master(
                size=str(payload.get("size", "")),
                holding_count=int(payload.get("holding_count", 0)),
                case_no=str(payload.get("case_no", "")),
                is_new=bool(payload.get("is_new", False)),
            )
            return self._ok({})
        except (TypeError, ValueError) as exc:
            return self._fail(AppValidationError(f"Invalid payload: {exc}"))
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def delete_pg_master(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            self._master_service.delete_pg_master(str(payload.get("size", "")))
            return self._ok({})
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def search_staff_master(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            rows = self._master_service.search_staff_master(str(payload.get("query", "")))
            return self._ok({"rows": self._serialize_rows(rows)})
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def update_staff_member(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            self._master_service.update_staff_member(
                staff_id=str(payload.get("staff_id", "")),
                name=str(payload.get("name", "")),
                department=str(payload.get("department", "")),
                kana=str(payload.get("kana", "")),
                visible=self._optional_bool(payload.get("visible", False)),
            )
            return self._ok({})
        except (AppConfigurationError, AppValidationError, AppDataAccessError) as exc:
            return self._fail(exc)

    def _ok(self, data: dict[str, Any]) -> dict[str, Any]:
        return {"ok": True, "data": data}

    def _fail(self, exc: Exception) -> dict[str, Any]:
        return {"ok": False, "error": exc.__class__.__name__, "message": str(exc) or exc.__class__.__name__}

    @staticmethod
    def _parse_date(value: Any) -> date | None:
        if value in {None, ""}:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value)[:10])

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        text = str(value).strip() if value is not None else ""
        return text or None

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        if value in {None, ""}:
            return None
        return int(value)

    @staticmethod
    def _optional_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if value is None:
            return False
        text = str(value).strip().lower()
        if text in {"1", "true", "yes", "on", "y"}:
            return True
        if text in {"0", "false", "no", "off", "n", ""}:
            return False
        return bool(value)

    def _serialize_rows(self, rows: Any) -> list[dict[str, Any]]:
        return [self._serialize_row(row) for row in rows]

    def _serialize_row(self, row: Any) -> dict[str, Any]:
        if isinstance(row, tuple) and len(row) == 2:
            return {
                "machine_code": self._serialize_value(row[0]),
                "returned_on": self._serialize_value(row[1]),
            }
        if is_dataclass(row):
            return {key: self._serialize_value(value) for key, value in asdict(row).items()}
        if isinstance(row, dict):
            return {key: self._serialize_value(value) for key, value in row.items()}
        data: dict[str, Any] = {}
        for key in dir(row):
            if key.startswith("_"):
                continue
            try:
                value = getattr(row, key)
            except AttributeError:
                continue
            if callable(value):
                continue
            data[key] = self._serialize_value(value)
        return data

    def _serialize_value(self, value: Any) -> Any:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if is_dataclass(value):
            return self._serialize_row(value)
        if isinstance(value, tuple):
            return [self._serialize_value(item) for item in value]
        if isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        return value
