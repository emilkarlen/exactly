from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Sequence, TypeVar, Generic

from exactly_lib.definitions import logic
from exactly_lib.test_case.result import pfh
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.logic_types import ExpectationType, from_is_negated
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


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
    return logic.NOT_OPERATOR_NAME + ' ' + instruction_arguments


def nothing__if_positive__not_option__if_negative(expectation_type: ExpectationType) -> str:
    return choice(expectation_type, '', logic.NOT_OPERATOR_NAME)


def prepend_not_operator_if_expectation_is_negative(instruction_arguments_without_not_option: str,
                                                    expectation_type: ExpectationType) -> str:
    if expectation_type is ExpectationType.NEGATIVE:
        return with_negation_argument(instruction_arguments_without_not_option)
    return instruction_arguments_without_not_option


class Case:
    def __init__(self,
                 expectation_type: ExpectationType,
                 negation_arguments: List,
                 main_result_assertion: Assertion[pfh.PassOrFailOrHardError]):
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
            Case(ExpectationType.NEGATIVE, [logic.NOT_OPERATOR_NAME],
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
        return self._value('', logic.NOT_OPERATOR_NAME)

    @property
    def empty__if_positive__not_option__if_negative(self) -> List[str]:
        return self._value([], [logic.NOT_OPERATOR_NAME])

    @property
    def pass__if_positive__fail__if_negative(self) -> Assertion[RET_TYPE]:
        return self.main_result(PassOrFail.PASS)

    @property
    def fail__if_positive__pass_if_negative(self) -> Assertion[RET_TYPE]:
        return self.main_result(PassOrFail.FAIL)

    @abstractmethod
    def main_result(self, expected_result_of_positive_test: PassOrFail
                    ) -> Assertion[RET_TYPE]:
        raise NotImplementedError('abstract method')

    def instruction_arguments(self, instruction_arguments_without_not_option: str) -> str:
        return prepend_not_operator_if_expectation_is_negative(instruction_arguments_without_not_option,
                                                               self._expectation_type_of_test_case)

    def _value(self,
               value_for_positive,
               value_for_negative):
        return value_for_positive if self.expectation_type is ExpectationType.POSITIVE else value_for_negative


class ExpectationTypeConfigForPfh(ExpectationTypeConfig[pfh.PassOrFailOrHardError]):
    def main_result(self, expected_result_of_positive_test: PassOrFail
                    ) -> Assertion[pfh.PassOrFailOrHardError]:
        return _MAIN_RESULT_ASSERTION_FOR_PFH[self._expectation_type_of_test_case][expected_result_of_positive_test]


class ExpectationTypeConfigForNoneIsSuccess(ExpectationTypeConfig[MatchingResult]):
    def main_result(self, expected_result_of_positive_test: PassOrFail
                    ) -> Assertion[MatchingResult]:
        return _MAIN_RESULT_ASSERTION__FROM_PASS_OR_FAIL[self._expectation_type_of_test_case][
            expected_result_of_positive_test]


def pfh_expectation_type_conf_from_is_negated(is_negated: bool) -> ExpectationTypeConfigForPfh:
    expectation_type = from_is_negated(is_negated)
    return ExpectationTypeConfigForPfh(expectation_type)


def pfh_expectation_type_config(expectation_type_of_test_case: ExpectationType) -> ExpectationTypeConfigForPfh:
    return ExpectationTypeConfigForPfh(expectation_type_of_test_case)


def expectation_type_config__non_is_success(expectation_type_of_test_case: ExpectationType
                                            ) -> ExpectationTypeConfigForNoneIsSuccess:
    return ExpectationTypeConfigForNoneIsSuccess(expectation_type_of_test_case)


_MAIN_RESULT_ASSERTION_FOR_PFH = {
    ExpectationType.POSITIVE: {
        PassOrFail.PASS: asrt_pfh.is_pass(),
        PassOrFail.FAIL: asrt_pfh.is_fail__with_arbitrary_message(),
    },
    ExpectationType.NEGATIVE: {
        PassOrFail.PASS: asrt_pfh.is_fail__with_arbitrary_message(),
        PassOrFail.FAIL: asrt_pfh.is_pass(),
    },
}

_ASSERT_IS_FAILURE_FOR_ERR_MSG = asrt.is_instance(str)

_MAIN_RESULT_ASSERTION__FROM_PASS_OR_FAIL = {
    ExpectationType.POSITIVE: {
        PassOrFail.PASS: asrt_matching_result.matches_value(True),
        PassOrFail.FAIL: asrt_matching_result.matches_value(False),
    },
    ExpectationType.NEGATIVE: {
        PassOrFail.PASS: asrt_matching_result.matches_value(False),
        PassOrFail.FAIL: asrt_matching_result.matches_value(True),
    },
}

MAIN_RESULT_ASSERTION__FROM_BOOL = {
    ExpectationType.POSITIVE: {
        True: asrt_matching_result.matches_value(True),
        False: asrt_matching_result.matches_value(False),
    },
    ExpectationType.NEGATIVE: {
        True: asrt_matching_result.matches_value(False),
        False: asrt_matching_result.matches_value(True),
    },
}
