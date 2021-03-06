from typing import Optional, Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


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
    def fails_pre_sds(err_msg: str = 'validation error/pre sds') -> 'ValidationActual':
        return ValidationActual(err_msg, None)

    @staticmethod
    def fails_post_sds(err_msg: str = 'validation error/post sds') -> 'ValidationActual':
        return ValidationActual(None, err_msg)


ValidationResultAssertion = Assertion[Optional[TextRenderer]]


def is_arbitrary_validation_failure() -> ValidationResultAssertion:
    return asrt.is_not_none_and(asrt_text_doc.is_any_text())


def is_validation_success() -> ValidationResultAssertion:
    return asrt.is_none


def matches_validation_failure(message: Assertion[str]) -> ValidationResultAssertion:
    return asrt_text_doc.is_string_for_test(message)


def new_single_string_text_for_test(text: str) -> TextRenderer:
    return asrt_text_doc.new_single_string_text_for_test(text)


class Expectation:
    def __init__(self,
                 passes_pre_sds: bool = True,
                 passes_post_sds: bool = True):
        self.passes_pre_sds = passes_pre_sds
        self.passes_post_sds = passes_post_sds

    @staticmethod
    def passes_all() -> 'Expectation':
        return Expectation(True, True)

    @staticmethod
    def pre_eds(result: bool) -> 'Expectation':
        return Expectation(result, True)

    @staticmethod
    def corresponding_to(actual: ValidationActual) -> 'Expectation':
        return Expectation(
            passes_pre_sds=actual.pre_sds is None,
            passes_post_sds=actual.post_sds is None,
        )


PRE_SDS_FAILURE_EXPECTATION = Expectation(False, True)
POST_SDS_FAILURE_EXPECTATION = Expectation(True, False)


class ValidationAssertions:
    def __init__(self,
                 pre_sds: ValidationResultAssertion,
                 post_sds: ValidationResultAssertion,
                 ):
        self._pre_sds = pre_sds
        self._post_sds = post_sds

    @staticmethod
    def corresponding_to(actual: ValidationActual) -> 'ValidationAssertions':
        return ValidationAssertions(
            pre_sds=assertion_from_actual(actual.pre_sds),
            post_sds=assertion_from_actual(actual.post_sds),
        )

    @staticmethod
    def all_passes() -> 'ValidationAssertions':
        return ValidationAssertions(
            pre_sds=asrt.is_none,
            post_sds=asrt.is_none,
        )

    @staticmethod
    def pre_sds_fails__w_any_msg() -> 'ValidationAssertions':
        return ValidationAssertions(
            pre_sds=asrt.is_not_none_and(asrt_text_doc.is_any_text()),
            post_sds=asrt.is_none,
        )

    @staticmethod
    def pre_sds_fails(expected_err_msg: Assertion[str] = asrt.anything_goes()
                      ) -> 'ValidationAssertions':
        return ValidationAssertions(
            pre_sds=asrt.is_not_none_and(asrt_text_doc.is_string_for_test(expected_err_msg)),
            post_sds=asrt.is_none,
        )

    @staticmethod
    def post_sds_fails(expected_err_msg: Assertion[str] = asrt.anything_goes()
                       ) -> 'ValidationAssertions':
        return ValidationAssertions(
            pre_sds=asrt.is_none,
            post_sds=asrt.is_not_none_and(asrt_text_doc.is_string_for_test(expected_err_msg)),
        )

    @staticmethod
    def post_sds_fails__w_any_msg() -> 'ValidationAssertions':
        return ValidationAssertions(
            pre_sds=asrt.is_none,
            post_sds=asrt.is_not_none_and(asrt_text_doc.is_any_text()),
        )

    @staticmethod
    def of_expectation(expectation: Expectation) -> 'ValidationAssertions':
        def mk_assertion(passes: bool) -> ValidationResultAssertion:
            return (
                asrt.is_none
                if passes
                else
                asrt.is_not_none_and(asrt_text_doc.is_any_text())
            )

        return ValidationAssertions(
            pre_sds=mk_assertion(expectation.passes_pre_sds),
            post_sds=mk_assertion(expectation.passes_post_sds),
        )

    @property
    def pre_sds(self) -> ValidationResultAssertion:
        return self._pre_sds

    @property
    def post_sds(self) -> ValidationResultAssertion:
        return self._post_sds


def assertion_from_actual(actual: Optional[str]) -> Assertion[Optional[TextRenderer]]:
    return (
        asrt.is_none
        if actual is None
        else
        asrt.is_not_none_and(asrt_text_doc.is_string_for_test(asrt.equals(actual)))
    )


def failing_validation_cases() -> Sequence[NEA[ValidationAssertions, ValidationActual]]:
    err_msg_pre_sds = 'validation err msg/pre sds'
    err_msg_post_sds = 'validation err msg/post sds'
    return [
        NEA('validation fails/pre sds',
            ValidationAssertions.pre_sds_fails(asrt.equals(err_msg_pre_sds)),
            ValidationActual.fails_pre_sds(err_msg_pre_sds),
            ),

        NEA('validation fails/post sds',
            ValidationAssertions.post_sds_fails(asrt.equals(err_msg_post_sds)),
            ValidationActual.fails_post_sds(err_msg_post_sds),
            ),
    ]
