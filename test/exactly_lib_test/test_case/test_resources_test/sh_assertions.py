import unittest

from exactly_lib.test_case.phases.result import sh
from exactly_lib_test.test_case.test_resources import sh_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsSuccess),
        unittest.makeSuite(TestIsHardError),
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
        actual = sh.new_sh_hard_error('failure msg')
        assertion = sut.is_success()
        # ACT #
        assert_that_assertion_fails(assertion, actual)


class TestIsHardError(unittest.TestCase):
    def test_pass(self):
        the_error_message = 'error message'
        cases = [
            ('no assertion on error message',
             sh.new_sh_hard_error(the_error_message),
             asrt.anything_goes(),
             ),
            ('assertion on error message',
             sh.new_sh_hard_error(the_error_message),
             asrt.equals(the_error_message),
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
             asrt.anything_goes(),
             ),
            ('assertion on error message fails',
             sh.new_sh_hard_error(the_error_message),
             asrt.equals(the_error_message + ' - part of message not in actual'),
             ),
        ]
        for name, actual, assertion_on_error_message in cases:
            with self.subTest(name=name):
                # ARRANGE #
                assertion = sut.is_hard_error(assertion_on_error_message)
                # ACT #
                assert_that_assertion_fails(assertion, actual)
