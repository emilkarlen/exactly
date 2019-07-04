import unittest

from exactly_lib.test_case.result import svh
from exactly_lib.util import file_printables
from exactly_lib.util.file_printer import FilePrintable
from exactly_lib_test.test_case.result.test_resources import svh_assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsSuccess),
        unittest.makeSuite(TestStatusIs),
        unittest.makeSuite(TestStatusIsNotSuccess),
    ])


class TestIsSuccess(unittest.TestCase):
    def test_success_WHEN_actual_is_success(self):
        # ARRANGE #
        assertion = sut.is_success()
        actual = svh.new_svh_success()
        # ACT #
        assertion.apply_without_message(self, actual)

    def test_success_WHEN_actual_is_not_success(self):
        # ARRANGE #
        cases = [
            NameAndValue('VALIDATION_ERROR',
                         svh.new_svh_validation_error(_printable_of_str('failure msg'))
                         ),
            NameAndValue('VALIDATION_ERROR/const msg',
                         svh.new_svh_validation_error__str('failure msg')
                         ),
            NameAndValue('HARD_ERROR',
                         svh.new_svh_hard_error(_printable_of_str('hard error msg'))
                         ),
            NameAndValue('HARD_ERROR/const msg',
                         svh.new_svh_hard_error__str('hard error msg')
                         ),
        ]
        assertion = sut.is_success()
        for case in cases:
            with self.subTest(case.name):
                # ACT #
                assert_that_assertion_fails(assertion, case.value)


class TestStatusIs(unittest.TestCase):
    def test_success_WHEN_actual_is_expected(self):
        # ARRANGE #
        cases = [
            NEA('SUCCESS',
                svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                svh.new_svh_success(),
                ),
            NEA('VALIDATION_ERROR',
                svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                svh.new_svh_validation_error(_printable_of_str('validation msg')),
                ),
            NEA('VALIDATION_ERROR/const msg',
                svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                svh.new_svh_validation_error__str('validation msg'),
                ),
            NEA('HARD_ERROR',
                svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR,
                svh.new_svh_hard_error(_printable_of_str('hard err msg')),
                ),
            NEA('HARD_ERROR/const msg',
                svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR,
                svh.new_svh_hard_error__str('hard err msg'),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assertion = sut.status_is(case.expected)
                # ACT & ASSERT #
                assertion.apply_without_message(self, case.actual)

    def test_unsuccessful_WHEN_actual_is_not_expected(self):
        # ARRANGE #
        cases = [
            NEA('SUCCESS',
                svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                svh.new_svh_validation_error(_printable_of_str('fail msg')),
                ),
            NEA('SUCCESS/const msg',
                svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                svh.new_svh_validation_error__str('fail msg'),
                ),
            NEA('VALIDATION_ERROR',
                svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                svh.new_svh_hard_error(_printable_of_str('hard err msg')),
                ),
            NEA('VALIDATION_ERROR/const msg',
                svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                svh.new_svh_hard_error__str('hard err msg'),
                ),
            NEA('HARD_ERROR',
                svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR,
                svh.new_svh_success(),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assertion = sut.status_is(case.expected)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, case.actual)


class TestStatusIsNotSuccess(unittest.TestCase):
    def test_success_WHEN_actual_is_expected(self):
        # ARRANGE #
        expected_err_msg = 'expected error message'
        cases = [
            NEA('VALIDATION/any error message',
                sut.status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR),
                svh.new_svh_validation_error__str(expected_err_msg),
                ),
            NEA('VALIDATION/matching error message',
                sut.status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                                          asrt.equals(expected_err_msg)),
                svh.new_svh_validation_error__str(expected_err_msg),
                ),
            NEA('HARD_ERROR/any error message',
                sut.status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR),
                svh.new_svh_hard_error__str(expected_err_msg),
                ),
            NEA('HARD_ERROR/matching error message',
                sut.status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR,
                                          asrt.equals(expected_err_msg)),
                svh.new_svh_hard_error__str(expected_err_msg),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                case.expected.apply_without_message(self, case.actual)

    def test_unsuccessful_WHEN_actual_is_not_expected(self):
        # ARRANGE #
        expected_err_msg = 'expected error message'
        actual_err_msg = 'actual error message'
        cases = [
            NEA('VALIDATION - SUCCESS/any error message',
                sut.status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR),
                svh.new_svh_success(),
                ),
            NEA('VALIDATION - VALIDATION/non-matching error message',
                sut.status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                                          asrt.equals(expected_err_msg)),
                svh.new_svh_validation_error(_printable_of_str(actual_err_msg)),
                ),
            NEA('VALIDATION - VALIDATION/non-matching error message/const msg',
                sut.status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                                          asrt.equals(expected_err_msg)),
                svh.new_svh_validation_error__str(actual_err_msg),
                ),
            NEA('HARD_ERROR - SUCCESS/any error message',
                sut.status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR),
                svh.new_svh_success(),
                ),
            NEA('HARD_ERROR - HARD_ERROR/non-matching error message',
                sut.status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR,
                                          asrt.equals(expected_err_msg)),
                svh.new_svh_hard_error(_printable_of_str(actual_err_msg)),
                ),
            NEA('HARD_ERROR - HARD_ERROR/non-matching error message/const msg',
                sut.status_is_not_success(svh.SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR,
                                          asrt.equals(expected_err_msg)),
                svh.new_svh_hard_error__str(actual_err_msg),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(case.expected, case.actual)


def _printable_of_str(s: str) -> FilePrintable:
    return file_printables.of_string(s)
