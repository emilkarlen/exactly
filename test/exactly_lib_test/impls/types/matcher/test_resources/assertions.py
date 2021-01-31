from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def main_result_is_success() -> Assertion[MatchingResult]:
    return asrt_matching_result.matches_value(True)


def main_result_is_failure() -> Assertion[MatchingResult]:
    return asrt_matching_result.matches_value(False)
