from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.matcher_checker import \
    MatcherPropertiesConfiguration

CHECKER__PARSE_FULL = integration_check.IntegrationChecker(
    parse_string_matcher.parsers().full,
    MatcherPropertiesConfiguration(),
    False,
)

CHECKER__PARSE_SIMPLE = integration_check.IntegrationChecker(
    parse_string_matcher.parsers().simple,
    MatcherPropertiesConfiguration(),
    False,
)
