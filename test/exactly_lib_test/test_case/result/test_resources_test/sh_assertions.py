import unittest

from exactly_lib.common.report_rendering.text_docs import single_pre_formatted_line_object
from exactly_lib.test_case.result import sh
from exactly_lib_test.common.test_resources import text_docs
from exactly_lib_test.test_case.result.test_resources import sh_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources import file_printable_assertions as asrt_file_printable


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
            ('no assertion on error message',
             sh.new_sh_hard_error__str(the_error_message),
             asrt_file_printable.matches(asrt.anything_goes()),
             ),
            ('assertion on error message',
             sh.new_sh_hard_error__str(the_error_message),
             asrt_file_printable.equals_string(the_error_message),
             ),
        ]
        for name, actual, assertion_on_error_message in cases:
            with self.subTest(name=name):
                # ARRANGE #
                assertion = sut.is_hard_error(assertion_on_error_message)
                # ACT #
                assertion.apply_without_message(self, actual)

    def test_fail(self):
        the_error_message = 'error message'
        cases = [
            ('is success',
             sh.new_sh_success(),
             asrt_file_printable.matches(asrt.anything_goes()),
             ),
            ('assertion on error message fails',
             sh.new_sh_hard_error__str(the_error_message),
             asrt_file_printable.equals_string(the_error_message + ' - part of message not in actual'),
             ),
        ]
        for name, actual, assertion_on_error_message in cases:
            with self.subTest(name=name):
                # ARRANGE #
                assertion = sut.is_hard_error(assertion_on_error_message)
                # ACT #
                assert_that_assertion_fails(assertion, actual)


class TestIsHardErrorAsTd(unittest.TestCase):
    def test_pass(self):
        the_error_message = 'error message'
        cases = [
            NEA('no assertion on error message',
                asrt.anything_goes(),
                sh.new_sh_hard_error__str(the_error_message),
                ),
            NEA('assertion on error message',
                text_docs.is_single_pre_formatted_text(asrt.equals(the_error_message)),
                sh.new_sh_hard_error__str(the_error_message),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ARRANGE #
                assertion = sut.is_hard_error__td(case.expected)
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
                text_docs.is_single_pre_formatted_text(asrt.equals(message_str)),
                sh.new_sh_hard_error__td(the_error_message),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ARRANGE #
                assertion = sut.is_hard_error__td(case.expected)
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
                text_docs.is_single_pre_formatted_text(
                    asrt.equals(the_error_message + ' - part of message not in actual')
                ),
                sh.new_sh_hard_error__str(the_error_message),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ARRANGE #
                assertion = sut.is_hard_error__td(case.expected)
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
                text_docs.is_single_pre_formatted_text(
                    asrt.equals(message_str + ' - part of message not in actual')
                ),
                sh.new_sh_hard_error__td(the_error_message),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ARRANGE #
                assertion = sut.is_hard_error__td(case.expected)
                # ACT #
                assert_that_assertion_fails(assertion, case.actual)
