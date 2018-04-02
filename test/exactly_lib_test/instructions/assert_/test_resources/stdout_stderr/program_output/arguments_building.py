from typing import List

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.assert_.utils.file_contents.stdout_stderr import OUTPUT_FROM_PROGRAM_OPTION_NAME
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_resources.arguments_building import OptionArgument


def from_program(program: ArgumentElements,
                 contents_matcher: List) -> ArgumentElements:
    return program \
        .prepend_to_first_line([OptionArgument(OUTPUT_FROM_PROGRAM_OPTION_NAME)]) \
        .followed_by_lines([list(contents_matcher)])


def negate_matcher(contents_matcher: List) -> List:
    return [instruction_arguments.NEGATION_ARGUMENT_STR] + contents_matcher


def matcher_for_expectation_type(expectation_type: ExpectationType,
                                 matcher: List) -> List:
    if expectation_type is ExpectationType.POSITIVE:
        return matcher
    else:
        return negate_matcher(matcher)


def emptiness_matcher() -> List:
    return [EMPTINESS_CHECK_ARGUMENT]
