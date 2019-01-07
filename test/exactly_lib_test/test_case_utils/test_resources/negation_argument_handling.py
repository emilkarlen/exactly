from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Sequence, TypeVar, Generic, Optional

from exactly_lib.definitions.instruction_arguments import NEGATION_ARGUMENT_STR
from exactly_lib.test_case.result import pfh
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.util.logic_types import ExpectationType, from_is_negated
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class PassOrFail(Enum):
    PASS = 0
    FAIL = 1


def pass_or_fail_from_bool(b: bool) -> PassOrFail:
    return PassOrFail.PASS if b else PassOrFail.FAIL


def choice(expectation_type: ExpectationType,
           value_for_positive,
           value_for_negative):
    return value_for_positive if expectation_type is ExpectationType.POSITIVE else value_for_negative


def with_negation_argument(instruction_arguments: str) -> str:
    return NEGATION_ARGUMENT_STR + ' ' + instruction_arguments


def nothing__if_positive__not_option__if_negative(expectation_type: ExpectationType) -> str:
    return choice(expectation_type, '', NEGATION_ARGUMENT_STR)


def prepend_not_operator_if_expectation_is_negative(instruction_arguments_without_not_option: str,
                                                    expectation_type: ExpectationType) -> str:
    if expectation_type is ExpectationType.NEGATIVE:
        return with_negation_argument(instruction_arguments_without_not_option)
    return instruction_arguments_without_not_option


class Case:
    def __init__(self,
                 expectation_type: ExpectationType,
                 negation_arguments: List,
                 main_result_assertion: ValueAssertion[pfh.PassOrFailOrHardError]):
        self.expectation_type = expectation_type
        self.negation_arguments = negation_arguments
        self.main_result_assertion = main_result_assertion


RET_TYPE = TypeVar('RET_TYPE')


class ExpectationTypeConfig(Generic[RET_TYPE], ABC):
    def __init__(self, expectation_type_of_test_case: ExpectationType):
        self._expectation_type_of_test_case = expectation_type_of_test_case

    def cases(self) -> Sequence[Case]:
        return [
            Case(ExpectationType.POSITIVE, [],
                 self.pass__if_positive__fail__if_negative
                 ),
            Case(ExpectationType.NEGATIVE, [NEGATION_ARGUMENT_STR],
                 self.fail__if_positive__pass_if_negative
                 ),
        ]

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
    def empty__if_positive__not_option__if_negative(self) -> List[str]:
        return self._value([], [NEGATION_ARGUMENT_STR])

    @property
    def pass__if_positive__fail__if_negative(self) -> ValueAssertion[RET_TYPE]:
        return self.main_result(PassOrFail.PASS)

    @property
    def fail__if_positive__pass_if_negative(self) -> ValueAssertion[RET_TYPE]:
        return self.main_result(PassOrFail.FAIL)

    @abstractmethod
    def main_result(self, expected_result_of_positive_test: PassOrFail
                    ) -> ValueAssertion[RET_TYPE]:
        pass

    def instruction_arguments(self, instruction_arguments_without_not_option: str) -> str:
        return prepend_not_operator_if_expectation_is_negative(instruction_arguments_without_not_option,
                                                               self._expectation_type_of_test_case)

    def _value(self,
               value_for_positive,
               value_for_negative):
        return value_for_positive if self.expectation_type is ExpectationType.POSITIVE else value_for_negative


class ExpectationTypeConfigForPfh(ExpectationTypeConfig[pfh.PassOrFailOrHardError]):
    def main_result(self, expected_result_of_positive_test: PassOrFail
                    ) -> ValueAssertion[pfh.PassOrFailOrHardError]:
        return _MAIN_RESULT_ASSERTION_FOR_PFH[self._expectation_type_of_test_case][expected_result_of_positive_test]


class ExpectationTypeConfigForNoneIsSuccess(ExpectationTypeConfig[Optional[ErrorMessageResolver]]):
    def main_result(self, expected_result_of_positive_test: PassOrFail
                    ) -> ValueAssertion[Optional[ErrorMessageResolver]]:
        return _MAIN_RESULT_ASSERTION_ERR_MSG_FOR_FAIL[self._expectation_type_of_test_case][
            expected_result_of_positive_test]


def pfh_expectation_type_conf_from_is_negated(is_negated: bool) -> ExpectationTypeConfigForPfh:
    expectation_type = from_is_negated(is_negated)
    return ExpectationTypeConfigForPfh(expectation_type)


def pfh_expectation_type_config(expectation_type_of_test_case: ExpectationType) -> ExpectationTypeConfigForPfh:
    return ExpectationTypeConfigForPfh(expectation_type_of_test_case)


def expectation_type_config__non_is_success(
        expectation_type_of_test_case: ExpectationType) -> ExpectationTypeConfigForNoneIsSuccess:
    return ExpectationTypeConfigForNoneIsSuccess(expectation_type_of_test_case)


_MAIN_RESULT_ASSERTION_FOR_PFH = {
    ExpectationType.POSITIVE: {
        PassOrFail.PASS: asrt_pfh.is_pass(),
        PassOrFail.FAIL: asrt_pfh.is_fail(),
    },
    ExpectationType.NEGATIVE: {
        PassOrFail.PASS: asrt_pfh.is_fail(),
        PassOrFail.FAIL: asrt_pfh.is_pass(),
    },
}

_ASSERT_IS_FAILURE_FOR_ERR_MSG = asrt.is_not_none_and_instance_with(ErrorMessageResolver, asrt.anything_goes())

_MAIN_RESULT_ASSERTION_ERR_MSG_FOR_FAIL = {
    ExpectationType.POSITIVE: {
        PassOrFail.PASS: asrt.is_none,
        PassOrFail.FAIL: _ASSERT_IS_FAILURE_FOR_ERR_MSG,
    },
    ExpectationType.NEGATIVE: {
        PassOrFail.PASS: _ASSERT_IS_FAILURE_FOR_ERR_MSG,
        PassOrFail.FAIL: asrt.is_none,
    },
}
