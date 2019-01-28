from typing import Optional

from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

ValidationResultAssertion = ValueAssertion[Optional[str]]


class Expectation:
    def __init__(self,
                 passes_pre_sds: bool = True,
                 passes_post_sds: bool = True):
        self.passes_pre_sds = passes_pre_sds
        self.passes_post_sds = passes_post_sds


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
