from exactly_lib.impls.types.program.parse import parse_program as sut
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.impls.types.program.test_resources import integration_check_config
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps import common_properties_checker

CHECKER_WO_EXECUTION = integration_check.IntegrationChecker(
    sut.program_parser(),
    integration_check_config.ProgramPropertiesConfiguration(
        common_properties_checker.ApplierThatDoesNothing(),
    ),
    True,
)
