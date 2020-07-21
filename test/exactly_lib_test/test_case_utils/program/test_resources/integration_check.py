from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.test_case_utils.program.test_resources import program_checker
from exactly_lib_test.test_case_utils.program.test_resources.assertions import ResultWithTransformationData


def checker_w_execution(consume_last_line_if_is_at_eol_after_parse: bool = True
                        ) -> IntegrationChecker[Program, ProcOutputFile, ResultWithTransformationData]:
    return IntegrationChecker(
        parse_program.program_parser(consume_last_line_if_is_at_eol_after_parse),
        program_checker.ProgramPropertiesConfiguration(
            program_checker.ExecutionApplier()
        )
    )


CHECKER_W_EXECUTION__CONSUME_LINE = checker_w_execution(consume_last_line_if_is_at_eol_after_parse=True)

CHECKER_W_EXECUTION__STAY_AT_END_OF_LINE = checker_w_execution(consume_last_line_if_is_at_eol_after_parse=False)

CHECKER_WO_EXECUTION__STAY_AT_END_OF_LINE = IntegrationChecker(
    parse_program.program_parser(consume_last_line_if_is_at_eol_after_parse=False),
    program_checker.ProgramPropertiesConfiguration(
        program_checker.NullApplier()
    )
)

SOURCE_CONSUMPTION_CASES__W_EXECUTION = [
    NameAndValue(
        'consume line',
        CHECKER_W_EXECUTION__CONSUME_LINE,
    ),
    NameAndValue(
        'stay at end of line',
        CHECKER_W_EXECUTION__STAY_AT_END_OF_LINE,
    ),
]
