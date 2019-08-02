from typing import Optional, Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.result import svh
from exactly_lib_test.test_case.result.test_resources import svh_assertions as asrt_svh
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc

ValidationResultAssertion = ValueAssertion[Optional[str]]


def is_arbitrary_validation_failure() -> ValueAssertion[Optional[str]]:
    return asrt.is_instance(str)


def is_validation_success() -> ValueAssertion[Optional[str]]:
    return asrt.is_none


def matches_validation_failure(message: ValueAssertion[str]) -> ValueAssertion[Optional[str]]:
    """Matcher on the resolved error message"""
    return asrt.is_instance_with(str, message)


class Expectation:
    def __init__(self,
                 passes_pre_sds: bool = True,
                 passes_post_sds: bool = True):
        self.passes_pre_sds = passes_pre_sds
        self.passes_post_sds = passes_post_sds


class ValidationActual:
    def __init__(self,
                 pre_sds: Optional[str] = None,
                 post_sds: Optional[str] = None):
        self.pre_sds = pre_sds
        self.post_sds = post_sds

    @staticmethod
    def passes():
        return ValidationActual(None, None)

    @staticmethod
    def fails_pre_sds(err_msg: str = 'validation error/pre sds'):
        return ValidationActual(err_msg, None)

    @staticmethod
    def fails_post_sds(err_msg: str = 'validation error/post sds'):
        return ValidationActual(None, err_msg)


def expect_passes_all_validations() -> Expectation:
    return Expectation(True, True)


def expect_validation_pre_eds(result: bool) -> Expectation:
    return Expectation(result, True)


class ValidationExpectation:
    def __init__(self,
                 pre_sds: ValidationResultAssertion,
                 post_sds: ValidationResultAssertion,
                 ):
        self._pre_sds = pre_sds
        self._post_sds = post_sds

    @property
    def pre_sds(self) -> ValidationResultAssertion:
        return self._pre_sds

    @property
    def post_sds(self) -> ValidationResultAssertion:
        return self._post_sds


def failing_validation_cases() -> Sequence[NEA[ValidationExpectation, ValidationActual]]:
    err_msg_pre_sds = 'validation err msg/pre sds'
    err_msg_post_sds = 'validation err msg/post sds'
    return [
        NEA('validation fails/pre sds',
            pre_sds_validation_fails(asrt.equals(err_msg_pre_sds)),
            ValidationActual.fails_pre_sds(err_msg_pre_sds),
            ),

        NEA('validation fails/post sds',
            post_sds_validation_fails(asrt.equals(err_msg_post_sds)),
            ValidationActual.fails_post_sds(err_msg_post_sds),
            ),
    ]


def all_validations_passes() -> ValidationExpectation:
    return ValidationExpectation(
        pre_sds=asrt.is_none,
        post_sds=asrt.is_none,
    )


def pre_sds_validation_fails(expected_err_msg: ValueAssertion[str] = asrt.anything_goes()
                             ) -> ValidationExpectation:
    return ValidationExpectation(
        pre_sds=asrt.is_not_none_and(expected_err_msg),
        post_sds=asrt.is_none,
    )


def post_sds_validation_fails(expected_err_msg: ValueAssertion[str] = asrt.anything_goes()
                              ) -> ValidationExpectation:
    return ValidationExpectation(
        pre_sds=asrt.is_none,
        post_sds=asrt.is_not_none_and(expected_err_msg),
    )


class ValidationExpectationSvh:
    def __init__(self,
                 pre_sds: ValueAssertion[svh.SuccessOrValidationErrorOrHardError],
                 post_sds: ValueAssertion[svh.SuccessOrValidationErrorOrHardError],
                 ):
        self._pre_sds = pre_sds
        self._post_sds = post_sds

    @property
    def pre_sds(self) -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
        return self._pre_sds

    @property
    def post_sds(self) -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
        return self._post_sds


def failing_validation_cases__svh() -> Sequence[NEA[ValidationExpectationSvh, ValidationActual]]:
    err_msg_pre_sds = 'validation err msg/pre sds'
    err_msg_post_sds = 'validation err msg/post sds'
    return [
        NEA('validation fails/pre sds',
            pre_sds_validation_fails__svh(asrt_text_doc.is_single_pre_formatted_text_that_equals(err_msg_pre_sds)),
            ValidationActual.fails_pre_sds(err_msg_pre_sds),
            ),

        NEA('validation fails/post sds',
            post_sds_validation_fails__svh(asrt_text_doc.is_single_pre_formatted_text_that_equals(err_msg_post_sds)),
            ValidationActual.fails_post_sds(err_msg_post_sds),
            ),
    ]


def all_validations_passes__svh() -> ValidationExpectationSvh:
    return ValidationExpectationSvh(
        pre_sds=asrt_svh.is_success(),
        post_sds=asrt_svh.is_success(),
    )


def pre_sds_validation_fails__svh(error_message: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text()
                                  ) -> ValidationExpectationSvh:
    return ValidationExpectationSvh(
        pre_sds=asrt_svh.is_validation_error(error_message),
        post_sds=asrt_svh.is_success(),
    )


def post_sds_validation_fails__svh(error_message: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text()
                                   ) -> ValidationExpectationSvh:
    return ValidationExpectationSvh(
        pre_sds=asrt_svh.is_success(),
        post_sds=asrt_svh.is_validation_error(error_message),
    )
