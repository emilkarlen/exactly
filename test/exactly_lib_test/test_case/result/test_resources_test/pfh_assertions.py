import unittest

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.test_case.result import pfh
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsPass),
        unittest.makeSuite(TestStatus),
        unittest.makeSuite(TestFailureMessage),
        unittest.makeSuite(TestIsFailWithArbitraryMessage),
        unittest.makeSuite(TestIsHardErrorWithArbitraryMessage),
    ])


class TestIsPass(unittest.TestCase):
    def test_success_WHEN_actual_is_pass(self):
        # ARRANGE #
        assertion = sut.is_pass()
        actual = pfh.new_pfh_pass()
        # ACT #
        assertion.apply_without_message(self, actual)

    def test_success_WHEN_actual_is_not_pass(self):
        # ARRANGE #
        cases = [
            NameAndValue('fail',
                         pfh.new_pfh_fail(asrt_text_doc.new_single_string_text_for_test('failure msg'))
                         ),
            NameAndValue('fail/const msg',
                         pfh.new_pfh_fail__str('failure msg')
                         ),
            NameAndValue('hard error',
                         pfh.new_pfh_hard_error(asrt_text_doc.new_single_string_text_for_test('hard error msg'))
                         ),
            NameAndValue('hard error/const msg',
                         pfh.new_pfh_hard_error__str('hard error msg')
                         ),
        ]
        assertion = sut.is_pass()
        for case in cases:
            with self.subTest(case.name):
                # ACT #
                assert_that_assertion_fails(assertion, case.value)


class TestStatus(unittest.TestCase):
    def test_success_WHEN_actual_is_expected(self):
        # ARRANGE #
        cases = [
            NEA('pass',
                sut.status_is(pfh.PassOrFailOrHardErrorEnum.PASS),
                pfh.new_pfh_pass(),
                ),
            NEA('fail',
                sut.status_is(pfh.PassOrFailOrHardErrorEnum.FAIL),
                pfh.new_pfh_fail(asrt_text_doc.new_single_string_text_for_test('fail msg')),
                ),
            NEA('fail/const msg',
                sut.status_is(pfh.PassOrFailOrHardErrorEnum.FAIL),
                pfh.new_pfh_fail__str('fail msg'),
                ),
            NEA('hard error',
                sut.status_is(pfh.PassOrFailOrHardErrorEnum.HARD_ERROR),
                pfh.new_pfh_hard_error(asrt_text_doc.new_single_string_text_for_test('hard err msg')),
                ),
            NEA('hard error/const msg',
                sut.status_is(pfh.PassOrFailOrHardErrorEnum.HARD_ERROR),
                pfh.new_pfh_hard_error__str('hard err msg'),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                case.expected.apply_without_message(self, case.actual)

    def test_unsuccessful_WHEN_actual_is_not_expected(self):
        # ARRANGE #
        cases = [
            NEA('pass',
                sut.status_is(pfh.PassOrFailOrHardErrorEnum.PASS),
                pfh.new_pfh_fail__str('fail msg'),
                ),
            NEA('fail',
                sut.status_is(pfh.PassOrFailOrHardErrorEnum.FAIL),
                pfh.new_pfh_hard_error__str('hard err msg'),
                ),
            NEA('hard error',
                sut.status_is(pfh.PassOrFailOrHardErrorEnum.HARD_ERROR),
                pfh.new_pfh_pass(),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(case.expected, case.actual)


class TestFailureMessage(unittest.TestCase):
    def test_success_WHEN_actual_is_expected(self):
        # ARRANGE #
        expected_err_msg = 'expected error message'
        cases = [
            NEA('fail',
                sut.failure_message_is(
                    asrt_text_doc.is_single_pre_formatted_text(asrt.equals(expected_err_msg))
                ),
                pfh.new_pfh_fail(asrt_text_doc.new_single_string_text_for_test(expected_err_msg)),
                ),
            NEA('fail/const msg',
                sut.failure_message_is(
                    asrt_text_doc.is_single_pre_formatted_text(asrt.equals(expected_err_msg))
                ),
                pfh.new_pfh_fail__str(expected_err_msg),
                ),
            NEA('hard error',
                sut.failure_message_is(
                    asrt_text_doc.is_single_pre_formatted_text(asrt.equals(expected_err_msg))
                ),
                pfh.new_pfh_hard_error(asrt_text_doc.new_single_string_text_for_test(expected_err_msg)),
                ),
            NEA('hard error/const msg',
                sut.failure_message_is(
                    asrt_text_doc.is_single_pre_formatted_text(asrt.equals(expected_err_msg))
                ),
                pfh.new_pfh_hard_error__str(expected_err_msg),
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
            NEA('fail',
                sut.failure_message_is(
                    asrt_text_doc.is_single_pre_formatted_text(asrt.equals(expected_err_msg))
                ),
                pfh.new_pfh_fail__str(actual_err_msg),
                ),
            NEA('hard error',
                sut.failure_message_is(
                    asrt_text_doc.is_single_pre_formatted_text(asrt.equals(expected_err_msg))
                ),
                pfh.new_pfh_hard_error__str(actual_err_msg),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(case.expected, case.actual)


class TestIsFailWithArbitraryMessage(unittest.TestCase):
    def test_success_WHEN_actual_is_expected(self):
        # ARRANGE #
        assertion = sut.is_fail__with_arbitrary_message()
        expected_err_msg = 'expected error message'
        cases = [
            NameAndValue('fail',
                         pfh.new_pfh_fail(asrt_text_doc.new_single_string_text_for_test(expected_err_msg)),
                         ),
            NameAndValue('fail/const msg',
                         pfh.new_pfh_fail__str(expected_err_msg),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assertion.apply_without_message(self, case.value)

    def test_unsuccessful_WHEN_actual_is_not_expected(self):
        # ARRANGE #
        assertion = sut.is_fail__with_arbitrary_message()
        cases = [
            NameAndValue('pass',
                         pfh.new_pfh_pass(),
                         ),
            NameAndValue('hard error',
                         pfh.new_pfh_hard_error__str('error message'),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, case.value)


class TestIsHardErrorWithArbitraryMessage(unittest.TestCase):
    def test_success_WHEN_actual_is_expected(self):
        # ARRANGE #
        assertion = sut.is_hard_error__with_arbitrary_message()
        expected_err_msg = 'expected error message'
        cases = [
            NameAndValue('hard error',
                         pfh.new_pfh_hard_error(asrt_text_doc.new_single_string_text_for_test(expected_err_msg)),
                         ),
            NameAndValue('hard error/const msg',
                         pfh.new_pfh_hard_error__str(expected_err_msg),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assertion.apply_without_message(self, case.value)

    def test_unsuccessful_WHEN_actual_is_not_expected(self):
        # ARRANGE #
        assertion = sut.is_hard_error__with_arbitrary_message()
        cases = [
            NameAndValue('pass',
                         pfh.new_pfh_pass(),
                         ),
            NameAndValue('fail',
                         pfh.new_pfh_fail__str('error message'),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, case.value)
