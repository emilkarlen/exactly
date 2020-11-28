from exactly_lib.impls.types.files_condition import parse
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.type_val_deps.types.files_condition.test_resources.properties_checker import \
    FilesConditionPropertiesConfiguration

CHECKER = integration_check.IntegrationChecker(
    parse.parsers().full,
    FilesConditionPropertiesConfiguration(),
    check_application_result_with_tcds=False,
)
