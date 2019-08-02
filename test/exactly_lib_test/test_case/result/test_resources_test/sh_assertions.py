import unittest

from exactly_lib.common.report_rendering.text_docs import single_pre_formatted_line_object
from exactly_lib.test_case.result import sh
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_case.result.test_resources import sh_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsSuccess),
        unittest.makeSuite(TestIsHardError),
        unittest.makeSuite(TestIsHardErrorAsTd),
    ])


class TestIsSuccess(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        assertion = sut.is_success()
        actual = sh.new_sh_success()
        # ACT #
        assertion.apply_without_message(self, actual)

    def test_fail(self):
        # ARRANGE #
        actual = sh.new_sh_hard_error__str('failure msg')
        assertion = sut.is_success()
        # ACT #
        assert_that_assertion_fails(assertion, actual)


class TestIsHardError(unittest.TestCase):
    def test_pass(self):
        the_error_message = 'error message'
        cases = [
            NEA('no assertion on error message contents',
                asrt.anything_goes(),
                sh.new_sh_hard_error__str(the_error_message),
                ),
            NEA('assertion on error message',
                asrt_text_doc.is_single_pre_formatted_text_that_equals(the_error_message),
                sh.new_sh_hard_error__str(the_error_message),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ARRANGE #
                assertion = sut.is_hard_error(case.expected)
                # ACT #
                assertion.apply_without_message(self, case.actual)

    def test_fail(self):
        the_error_message = 'error message'
        cases = [
            NEA('is success',
                asrt.anything_goes(),
                sh.new_sh_success(),
                ),
            NEA('assertion on error message fails',
                asrt_text_doc.is_single_pre_formatted_text_that_equals(
                    the_error_message + ' - part of message not in actual'
                ),
                sh.new_sh_hard_error__str(the_error_message),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ARRANGE #
                assertion = sut.is_hard_error(case.expected)
                # ACT #
                assert_that_assertion_fails(assertion, case.actual)


class TestIsHardErrorAsTd(unittest.TestCase):
    def test_pass(self):
        the_error_message = 'error message'
        cases = [
            NEA('no assertion on error message',
                asrt.anything_goes(),
                sh.new_sh_hard_error__str(the_error_message),
                ),
            NEA('assertion on error message',
                asrt_text_doc.is_single_pre_formatted_text_that_equals(the_error_message),
                sh.new_sh_hard_error__str(the_error_message),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ARRANGE #
                assertion = sut.is_hard_error(case.expected)
                # ACT #
                assertion.apply_without_message(self, case.actual)

    def test_pass__value_from_td(self):
        message_str = 'error message'
        the_error_message = single_pre_formatted_line_object(message_str)
        cases = [
            NEA('no assertion on error message',
                asrt.anything_goes(),
                sh.new_sh_hard_error__td(the_error_message),
                ),
            NEA('assertion on error message',
                asrt_text_doc.is_single_pre_formatted_text_that_equals(message_str),
                sh.new_sh_hard_error__td(the_error_message),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ARRANGE #
                assertion = sut.is_hard_error(case.expected)
                # ACT #
                assertion.apply_without_message(self, case.actual)

    def test_fail(self):
        the_error_message = 'error message'
        cases = [
            NEA('is success',
                asrt.anything_goes(),
                sh.new_sh_success(),
                ),
            NEA('assertion on error message fails',
                asrt_text_doc.is_single_pre_formatted_text_that_equals(
                    the_error_message + ' - part of message not in actual'
                ),
                sh.new_sh_hard_error__str(the_error_message),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ARRANGE #
                assertion = sut.is_hard_error(case.expected)
                # ACT #
                assert_that_assertion_fails(assertion, case.actual)

    def test_fail__value_from_td(self):
        message_str = 'error message'
        the_error_message = single_pre_formatted_line_object(message_str)
        cases = [
            NEA('is success',
                asrt.anything_goes(),
                sh.new_sh_success(),
                ),
            NEA('assertion on error message fails',
                asrt_text_doc.is_single_pre_formatted_text_that_equals(
                    message_str + ' - part of message not in actual'
                ),
                sh.new_sh_hard_error__td(the_error_message),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ARRANGE #
                assertion = sut.is_hard_error(case.expected)
                # ACT #
                assert_that_assertion_fails(assertion, case.actual)
