import sys

from exactly_lib.cli.definitions import common_cli_options
from exactly_lib_test.processing.test_resources.test_case_setup import instruction_set_with_no_instructions

ARGUMENTS_FOR_TEST_INTERPRETER_TUPLE = (common_cli_options.OPTION_FOR_ACTOR, sys.executable)
ARGUMENTS_FOR_TEST_INTERPRETER = list(ARGUMENTS_FOR_TEST_INTERPRETER_TUPLE)


def arguments_for_test_interpreter_and_more_tuple(additional_args: iter) -> tuple:
    return ARGUMENTS_FOR_TEST_INTERPRETER_TUPLE + tuple(additional_args)


def first_char_is_name_and_rest_is_argument__splitter(s: str) -> str:
    return s[0]


EMPTY_INSTRUCTIONS_SETUP = instruction_set_with_no_instructions()
