from typing import Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.result import svh
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.test_resources.validation.validation import Expectation, ValidationActual
from exactly_lib_test.test_case.result.test_resources import svh_assertions as asrt_svh
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class ValidationExpectationSvh:
    def __init__(self,
                 pre_sds: Assertion[svh.SuccessOrValidationErrorOrHardError],
                 post_sds: Assertion[svh.SuccessOrValidationErrorOrHardError],
                 ):
        self._pre_sds = pre_sds
        self._post_sds = post_sds

    @staticmethod
    def of_plain(plain: Expectation) -> 'ValidationExpectationSvh':
        return ValidationExpectationSvh(
            pre_sds=_svh_from_bool(plain.passes_pre_sds),
            post_sds=_svh_from_bool(plain.passes_post_sds),
        )

    @staticmethod
    def passes() -> 'ValidationExpectationSvh':
        return ValidationExpectationSvh(
            pre_sds=asrt_svh.is_success(),
            post_sds=asrt_svh.is_success(),
        )

    @staticmethod
    def fails__pre_sds(error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text()
                       ) -> 'ValidationExpectationSvh':
        return ValidationExpectationSvh(
            pre_sds=asrt_svh.is_validation_error(error_message),
            post_sds=asrt_svh.is_success(),
        )

    @staticmethod
    def fails__post_sds(error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text()
                        ) -> 'ValidationExpectationSvh':
        return ValidationExpectationSvh(
            pre_sds=asrt_svh.is_success(),
            post_sds=asrt_svh.is_validation_error(error_message),
        )

    @staticmethod
    def hard_error__post_sds(error_message: Assertion[TextRenderer] = asrt_text_doc.is_any_text()
                             ) -> 'ValidationExpectationSvh':
        return ValidationExpectationSvh(
            pre_sds=asrt_svh.is_success(),
            post_sds=asrt_svh.is_hard_error(error_message),
        )

    @property
    def pre_sds(self) -> Assertion[svh.SuccessOrValidationErrorOrHardError]:
        return self._pre_sds

    @property
    def post_sds(self) -> Assertion[svh.SuccessOrValidationErrorOrHardError]:
        return self._post_sds


def failing_validation_cases__svh() -> Sequence[NEA[ValidationExpectationSvh, ValidationActual]]:
    err_msg_pre_sds = 'validation err msg/pre sds'
    err_msg_post_sds = 'validation err msg/post sds'
    return [
        NEA('validation fails/pre sds',
            ValidationExpectationSvh.fails__pre_sds(asrt_text_doc.is_string_for_test_that_equals(err_msg_pre_sds)),
            ValidationActual.fails_pre_sds(err_msg_pre_sds),
            ),

        NEA('validation fails/post sds',
            ValidationExpectationSvh.fails__post_sds(asrt_text_doc.is_string_for_test_that_equals(err_msg_post_sds)),
            ValidationActual.fails_post_sds(err_msg_post_sds),
            ),
    ]


def _svh_from_bool(passes_validation: bool) -> Assertion[svh.SuccessOrValidationErrorOrHardError]:
    return (
        asrt_svh.is_success()
        if passes_validation
        else
        asrt_svh.is_validation_error()
    )
