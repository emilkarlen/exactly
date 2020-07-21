from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.test_case_utils.program.test_resources import program_checker

CHECKER_W_EXECUTION = IntegrationChecker(
    parse_program.program_parser(),
    program_checker.ProgramPropertiesConfiguration(
        program_checker.ExecutionApplier()
    )
)

CHECKER_WO_EXECUTION = IntegrationChecker(
    parse_program.program_parser(),
    program_checker.ProgramPropertiesConfiguration(
        program_checker.NullApplier()
    )
)
