import unittest

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.test_case_utils import svh_exception as sut
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_case.result.test_resources import svh_assertions as asrt_svh


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
        expectation = asrt_svh.is_validation_error(
            asrt_text_doc.is_single_pre_formatted_text_that_equals(error_message)
        )
        expectation.apply_without_message(self, actual)

    def test_hard_error(self):
        # ARRANGE #
        error_message = 'hard error'
        # ACT #
        actual = sut.translate_svh_exception_to_svh(test_action, DO_HARD_ERROR, error_message)
        # ASSERT #
        expectation = asrt_svh.is_hard_error(
            asrt_text_doc.is_single_pre_formatted_text_that_equals(error_message)
        )
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
        raise sut.SvhHardErrorException(text_docs.single_pre_formatted_line_object(message))
    if what_to_do == DO_VALIDATION_ERROR:
        raise sut.SvhValidationException(text_docs.single_pre_formatted_line_object(message))
    if what_to_do != DO_SUCCESS:
        raise ValueError('unexpected what_to_do: ' + str(what_to_do))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
