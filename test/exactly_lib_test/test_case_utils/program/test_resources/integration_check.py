from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check as logic_integration_check
from exactly_lib_test.test_case_utils.program.test_resources.program_checker import ProgramPropertiesConfiguration

CHECKER__CONSUME_LINE = logic_integration_check.IntegrationChecker(
    parse_program.program_parser(consume_last_line_if_is_at_eol_after_parse=True),
    ProgramPropertiesConfiguration()
)

CHECKER__STAY_AT_END_OF_LINE = logic_integration_check.IntegrationChecker(
    parse_program.program_parser(consume_last_line_if_is_at_eol_after_parse=False),
    ProgramPropertiesConfiguration()
)

SOURCE_CONSUMPTION_CASES = [
    NameAndValue(
        'consume line',
        CHECKER__CONSUME_LINE,
    ),
    NameAndValue(
        'stay at end of line',
        CHECKER__STAY_AT_END_OF_LINE,
    ),
]
