import sys

from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_ACTOR
from exactly_lib.processing.instruction_setup import InstructionsSetup

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
