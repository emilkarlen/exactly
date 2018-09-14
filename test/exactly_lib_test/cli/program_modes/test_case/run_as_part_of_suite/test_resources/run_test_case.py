from pathlib import Path

from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram, TestSuiteDefinition
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib_test.cli.program_modes.test_case.run_as_part_of_suite.test_resources.cli_args import cli_args_for
from exactly_lib_test.cli.program_modes.test_resources.main_program_execution import main_program_of, \
    capture_output_from_main_program
from exactly_lib_test.test_resources.process import SubProcessResult


def run_test_case(parsing_setup: TestCaseParsingSetup,
                  test_case_handling_setup: TestCaseHandlingSetup,
                  test_suite_definition: TestSuiteDefinition,
                  case_file: Path,
                  suite_file: Path) -> SubProcessResult:
    test_case_definition_for_main_program = TestCaseDefinitionForMainProgram(
        parsing_setup,
        [])

    main_pgm = main_program_of(test_case_definition_for_main_program,
                               test_suite_definition,
                               test_case_handling_setup)

    command_line_arguments = cli_args_for(
        suite_file=str(suite_file),
        case_file=str(case_file),
    )

    return capture_output_from_main_program(command_line_arguments,
                                            main_pgm)
