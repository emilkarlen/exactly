from exactly_lib.impls.types.files_condition import parse
from exactly_lib_test.impls.types.files_condition.test_resources.properties_checker import \
    FilesConditionPropertiesConfiguration
from exactly_lib_test.impls.types.logic.test_resources import integration_check

CHECKER = integration_check.IntegrationChecker(
    parse.parsers().full,
    FilesConditionPropertiesConfiguration(),
    False,
)
