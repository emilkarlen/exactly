import unittest

from exactly_lib.instructions.utils import return_svh_via_exceptions as sut
from exactly_lib_test.test_case_utils.test_resources import svh_assertions as asrt_svh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_success(self):
        # ARRANGE #
        error_message = 'validation error'
        # ACT #
        actual = sut.translate_svh_exception_to_svh(test_action, DO_SUCCESS, error_message)
        # ASSERT #
        expectation = asrt_svh.is_success()
        expectation.apply_without_message(self, actual)

    def test_validation_error(self):
        # ARRANGE #
        error_message = 'validation error'
        # ACT #
        actual = sut.translate_svh_exception_to_svh(test_action, DO_VALIDATION_ERROR, error_message)
        # ASSERT #
        expectation = asrt_svh.is_validation_error(asrt.equals(error_message))
        expectation.apply_without_message(self, actual)

    def test_hard_error(self):
        # ARRANGE #
        error_message = 'hard error'
        # ACT #
        actual = sut.translate_svh_exception_to_svh(test_action, DO_HARD_ERROR, error_message)
        # ASSERT #
        expectation = asrt_svh.is_hard_error(asrt.equals(error_message))
        expectation.apply_without_message(self, actual)

    def test_raises_exception_when_called_with_wrong_arguments(self):
        # ACT #
        with self.assertRaises(Exception):
            sut.translate_svh_exception_to_svh(test_action, DO_VALIDATION_ERROR, 'error message',
                                               'unexpected argument')


DO_SUCCESS = 0

DO_VALIDATION_ERROR = 1

DO_HARD_ERROR = 2


def test_action(what_to_do: int, message: str):
    if what_to_do == DO_HARD_ERROR:
        raise sut.SvhHardErrorException(message)
    if what_to_do == DO_VALIDATION_ERROR:
        raise sut.SvhValidationException(message)
    if what_to_do != DO_SUCCESS:
        raise ValueError('unexpected what_to_do: ' + str(what_to_do))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
