import unittest

from exactly_lib.instructions.assert_.utils import return_pfh_via_exceptions as sut
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check as asrt_pfh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        error_message = 'should not be raised error'
        # ACT #
        actual = sut.translate_pfh_exception_to_pfh(test_action, DO_SUCCESS, error_message)
        # ASSERT #
        expectation = asrt_pfh.is_pass()
        expectation.apply_without_message(self, actual)

    def test_fail_error(self):
        # ARRANGE #
        error_message = 'validation error'
        # ACT #
        actual = sut.translate_pfh_exception_to_pfh(test_action, DO_FAIL, error_message)
        # ASSERT #
        expectation = asrt_pfh.is_fail(asrt.equals(error_message))
        expectation.apply_without_message(self, actual)

    def test_hard_error(self):
        # ARRANGE #
        error_message = 'hard error'
        # ACT #
        actual = sut.translate_pfh_exception_to_pfh(test_action, DO_HARD_ERROR, error_message)
        # ASSERT #
        expectation = asrt_pfh.is_hard_error(asrt.equals(error_message))
        expectation.apply_without_message(self, actual)

    def test_raises_exception_when_called_with_wrong_arguments(self):
        # ACT #
        with self.assertRaises(Exception):
            sut.translate_pfh_exception_to_pfh(test_action, DO_FAIL, 'error message',
                                               'unexpected argument')


DO_SUCCESS = 0

DO_FAIL = 1

DO_HARD_ERROR = 2


def test_action(what_to_do: int, message: str):
    if what_to_do == DO_HARD_ERROR:
        raise sut.PfhHardErrorException(message)
    if what_to_do == DO_FAIL:
        raise sut.PfhFailException(message)
    if what_to_do != DO_SUCCESS:
        raise ValueError('unexpected what_to_do: ' + str(what_to_do))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
