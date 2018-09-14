from pathlib import Path
from typing import Optional, List

from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram, TestSuiteDefinition
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib_test.cli.program_modes.test_case.run_as_part_of_suite.test_resources import cli_args
from exactly_lib_test.cli.program_modes.test_resources.main_program_execution import main_program_of, \
    capture_output_from_main_program
from exactly_lib_test.test_resources.process import SubProcessResult


def run_test_case(parsing_setup: TestCaseParsingSetup,
                  test_case_handling_setup: TestCaseHandlingSetup,
                  test_suite_definition: TestSuiteDefinition,
                  case_file: Path,
                  suite_file: Optional[Path]) -> SubProcessResult:
    def command_line_arguments() -> List[str]:
        if suite_file is None:
            return cli_args.cli_args_for_implicit_default_suite(str(case_file))
        else:
            return cli_args.cli_args_for_explicit_suite(suite_file=str(suite_file),
                                                        case_file=str(case_file))

    test_case_definition_for_main_program = TestCaseDefinitionForMainProgram(
        parsing_setup,
        [])

    main_pgm = main_program_of(test_case_definition_for_main_program,
                               test_suite_definition,
                               test_case_handling_setup)

    return capture_output_from_main_program(command_line_arguments(),
                                            main_pgm)
