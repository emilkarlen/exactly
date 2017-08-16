from enum import Enum

from exactly_lib.instructions.assert_.utils.negation_of_assertion import NEGATION_ARGUMENT_STR
from exactly_lib.instructions.utils.expectation_type import ExpectationType, from_is_negated
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check as asrt_pfh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class PassOrFail(Enum):
    PASS = 0
    FAIL = 1


def with_negation_argument(instruction_arguments: str) -> str:
    return NEGATION_ARGUMENT_STR + ' ' + instruction_arguments


def prepend_not_operator_if_expectation_is_negative(instruction_arguments_without_not_option: str,
                                                    expectation_type: ExpectationType) -> str:
    if expectation_type is ExpectationType.NEGATIVE:
        return NEGATION_ARGUMENT_STR + ' ' + instruction_arguments_without_not_option
    return instruction_arguments_without_not_option


class ExpectationTypeConfig:
    def __init__(self, expectation_type_of_test_case: ExpectationType):
        self._expectation_type_of_test_case = expectation_type_of_test_case

    @property
    def expectation_type(self) -> ExpectationType:
        return self._expectation_type_of_test_case

    @property
    def expectation_type_str(self) -> str:
        return str(self._expectation_type_of_test_case)

    def __str__(self) -> str:
        return 'expectation_type=' + self.expectation_type_str

    @property
    def nothing__if_positive__not_option__if_negative(self) -> str:
        return self._value('', NEGATION_ARGUMENT_STR)

    @property
    def pass__if_positive__fail__if_negative(self) -> asrt.ValueAssertion:
        return self.main_result(PassOrFail.PASS)

    @property
    def fail__if_positive__pass_if_negative(self) -> asrt.ValueAssertion:
        return self.main_result(PassOrFail.FAIL)

    def main_result(self, expected_result_of_positive_test: PassOrFail) -> asrt.ValueAssertion:
        return _MAIN_RESULT_ASSERTION[self._expectation_type_of_test_case][expected_result_of_positive_test]

    def instruction_arguments(self, instruction_arguments_without_not_option: str) -> str:
        return prepend_not_operator_if_expectation_is_negative(instruction_arguments_without_not_option,
                                                               self._expectation_type_of_test_case)

    def _value(self,
               value_for_positive,
               value_for_negative):
        return value_for_positive if self.expectation_type is ExpectationType.POSITIVE else value_for_negative


def expectation_type_conf_from_is_negated(is_negated: bool) -> ExpectationTypeConfig:
    expectation_type = from_is_negated(is_negated)
    return ExpectationTypeConfig(expectation_type)


_MAIN_RESULT_ASSERTION = {
    ExpectationType.POSITIVE: {
        PassOrFail.PASS: asrt_pfh.is_pass(),
        PassOrFail.FAIL: asrt_pfh.is_fail(),
    },
    ExpectationType.NEGATIVE: {
        PassOrFail.PASS: asrt_pfh.is_fail(),
        PassOrFail.FAIL: asrt_pfh.is_pass(),
    },
}
