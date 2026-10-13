from datetime import date
import unittest
from unittest.mock import Mock

from app.application.usecases.master_usecase import MasterUseCase
from app.application.usecases.operation_usecase import OperationUseCase
from app.shared.errors import ValidationError
from app.utils.errors import AppValidationError
from app.utils.validators import (
    normalize_gauge_sizes, validate_confirmation_case_no,
    validate_lending_registration, validate_return_case_no,
)


class BusinessRulesTests(unittest.TestCase):
    def test_size_normalization(self):
        self.assertEqual(normalize_gauge_sizes([" a1 ", "", "  ", "b2"]), ["A1", "B2"])

    def test_registration_requires_a_size(self):
        with self.assertRaises(AppValidationError):
            validate_lending_registration(
                lent_on=date(2026, 10, 13), machine_prefix="A", machine_suffix="1",
                staff_id="test", gauge_sizes=["", " "],
            )

    def test_return_case_boundary(self):
        self.assertEqual(validate_return_case_no(" a1 "), "A1")
        for value in ("", " ", "ABC"):
            with self.subTest(value=value), self.assertRaises(AppValidationError):
                validate_return_case_no(value)

    def test_confirmation_case_boundary(self):
        self.assertEqual(validate_confirmation_case_no("a" * 20), "A" * 20)
        for value in ("", " ", "a" * 21):
            with self.subTest(value=value), self.assertRaises(AppValidationError):
                validate_confirmation_case_no(value)

    def test_invalid_return_never_writes(self):
        repository = Mock()
        usecase = OperationUseCase(repository)
        with self.assertRaises(ValidationError):
            usecase.return_one_loan(loan_id=None, case_no="A1", returned_on=date(2026, 10, 13))
        repository.return_one_loan.assert_not_called()

    def test_referenced_master_never_deleted(self):
        repository = Mock()
        repository.count_pg_master_references.return_value = 1
        with self.assertRaises(ValidationError):
            MasterUseCase(repository).delete_pg_master(" a1 ")
        repository.count_pg_master_references.assert_called_once_with("A1")
        repository.delete_pg_master.assert_not_called()

    def test_unreferenced_master_deletion(self):
        repository = Mock()
        repository.count_pg_master_references.return_value = 0
        MasterUseCase(repository).delete_pg_master(" a1 ")
        repository.delete_pg_master.assert_called_once_with("A1")
