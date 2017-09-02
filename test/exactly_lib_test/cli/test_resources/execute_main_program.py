import sys

from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_ACTOR
from exactly_lib.default import default_main_program as sut
from exactly_lib.default.program_modes.test_suite import test_suite_definition
from exactly_lib.execution.full_execution import PredefinedProperties
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles

ARGUMENTS_FOR_TEST_INTERPRETER_TUPLE = (OPTION_FOR_ACTOR, sys.executable)

ARGUMENTS_FOR_TEST_INTERPRETER = list(ARGUMENTS_FOR_TEST_INTERPRETER_TUPLE)


def arguments_for_test_interpreter_and_more_tuple(additional_args: iter) -> tuple:
    return ARGUMENTS_FOR_TEST_INTERPRETER_TUPLE + tuple(additional_args)


def first_char_is_name_and_rest_is_argument__splitter(s: str) -> str:
    return s[0]


EMPTY_INSTRUCTIONS_SETUP = InstructionsSetup(
    {},
    {},
    {},
    {},
    {})


def execute_main_program(arguments: list,
                         the_test_case_handling_setup: TestCaseHandlingSetup,
                         instructions_setup: InstructionsSetup = EMPTY_INSTRUCTIONS_SETUP,
                         name_and_argument_splitter=first_char_is_name_and_rest_is_argument__splitter,
                         predefined_properties: PredefinedProperties = PredefinedProperties(),
                         ) -> SubProcessResult:
    str_std_out_files = StringStdOutFiles()
    program = sut.MainProgram(str_std_out_files.stdout_files,
                              TestCaseDefinition(
                                  name_and_argument_splitter,
                                  instructions_setup,
                                  predefined_properties,
                              ),
                              test_suite_definition(),
                              the_test_case_handling_setup)
    exit_status = program.execute(arguments)
    str_std_out_files.finish()
    return SubProcessResult(exit_status,
                            str_std_out_files.stdout_contents,
                            str_std_out_files.stderr_contents)
