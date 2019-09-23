from typing import List

import exactly_lib.definitions.primitives.file_or_dir_contents
from exactly_lib.definitions import instruction_arguments
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.test_resources.arguments_building import Stringable


def negate_matcher(contents_matcher: List[Stringable]) -> List[Stringable]:
    return [instruction_arguments.NEGATION_ARGUMENT_STR] + contents_matcher


def matcher_for_expectation_type(expectation_type: ExpectationType,
                                 matcher: List) -> List[Stringable]:
    if expectation_type is ExpectationType.POSITIVE:
        return matcher
    else:
        return negate_matcher(matcher)


def emptiness_matcher() -> List[Stringable]:
    return [exactly_lib.definitions.primitives.file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT]


def equals_matcher(expected) -> List[Stringable]:
    return [matcher_options.EQUALS_ARGUMENT, expected]
