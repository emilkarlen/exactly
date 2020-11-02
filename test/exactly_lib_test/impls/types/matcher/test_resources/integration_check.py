from typing import Callable, TypeVar

from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import ExecutionExpectation, Expectation
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result

MODEL = TypeVar('MODEL')


def is_expectation_of_execution_result_of(expected: bool) -> Expectation[MatcherWTrace[MODEL], MatchingResult]:
    return Expectation(
        execution=ExecutionExpectation(
            main_result=asrt_matching_result.matches_value(expected)
        )
    )


def is_pass() -> Expectation[MatcherWTrace[MODEL], MatchingResult]:
    return is_expectation_of_execution_result_of(True)


EXECUTION_IS_PASS = ExecutionExpectation(
    main_result=asrt_matching_result.matches_value(True)
)


def constant_model(model: MODEL) -> Callable[[FullResolvingEnvironment], MODEL]:
    def ret_val(environment: FullResolvingEnvironment) -> MODEL:
        return model

    return ret_val
