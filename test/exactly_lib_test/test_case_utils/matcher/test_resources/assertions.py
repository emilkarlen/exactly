from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


def main_result_is_success() -> ValueAssertion[MatchingResult]:
    return asrt_matching_result.matches_value(True)


def main_result_is_failure() -> ValueAssertion[MatchingResult]:
    return asrt_matching_result.matches_value(False)
