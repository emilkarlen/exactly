from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check as logic_integration_check
from exactly_lib_test.test_case_utils.program.test_resources.program_checker import ProgramPropertiesConfiguration

CHECKER = logic_integration_check.IntegrationChecker(
    parse_program.program_parser(),
    ProgramPropertiesConfiguration()
)
