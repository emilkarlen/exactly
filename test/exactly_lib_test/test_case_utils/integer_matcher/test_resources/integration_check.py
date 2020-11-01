from typing import Callable

from exactly_lib.test_case_utils.integer_matcher import parse_integer_matcher
from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.matcher_checker import \
    MatcherPropertiesConfiguration

ModelConstructor = Callable[[FullResolvingEnvironment], int]


def constant(value: int) -> ModelConstructor:
    def ret_val(environment: FullResolvingEnvironment) -> int:
        return value

    return ret_val


ARBITRARY_MODEL = constant(0)

CHECKER__PARSE_FULL = integration_check.IntegrationChecker(
    parse_integer_matcher.parsers().full,
    MatcherPropertiesConfiguration(),
    False,
)

CHECKER__PARSE_SIMPLE = integration_check.IntegrationChecker(
    parse_integer_matcher.parsers().simple,
    MatcherPropertiesConfiguration(),
    False,
)
