from exactly_lib.impls.types.program.parse import parse_program as sut
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.impls.types.program.test_resources import integration_check_applier
from exactly_lib_test.impls.types.program.test_resources import integration_check_config

CHECKER_WO_EXECUTION = integration_check.IntegrationChecker(
    sut.program_parser(),
    integration_check_config.ProgramPropertiesConfiguration(
        integration_check_applier.NullApplier(),
    ),
    True,
)
