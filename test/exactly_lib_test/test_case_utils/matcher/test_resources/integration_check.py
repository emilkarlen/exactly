from typing import Callable, TypeVar

from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import Expectation, ExecutionExpectation
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result

MODEL = TypeVar('MODEL')


def is_expectation_of_execution_result_of(expected: bool) -> Expectation[MatchingResult]:
    return Expectation(
        execution=ExecutionExpectation(
            main_result=asrt_matching_result.matches_value(expected)
        )
    )


def is_pass() -> Expectation[MatchingResult]:
    return is_expectation_of_execution_result_of(True)


def constant_model(model: MODEL) -> Callable[[FullResolvingEnvironment], MODEL]:
    def ret_val(environment: FullResolvingEnvironment) -> MODEL:
        return model

    return ret_val
