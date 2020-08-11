from exactly_lib.test_case_utils.files_matcher import parse_files_matcher
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check
from exactly_lib_test.test_case_utils.matcher.test_resources.matcher_checker import \
    MatcherPropertiesConfiguration

CHECKER = integration_check.IntegrationChecker(
    parse_files_matcher.files_matcher_parser(),
    MatcherPropertiesConfiguration(),
    False,
)
