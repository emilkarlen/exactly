from exactly_lib.test_case_utils.files_condition import parse
from exactly_lib_test.test_case_utils.files_condition.test_resources.properties_checker import \
    FilesConditionPropertiesConfiguration
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check

CHECKER = integration_check.IntegrationChecker(
    parse.parser(),
    FilesConditionPropertiesConfiguration(),
)
