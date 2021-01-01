from typing import List

from exactly_lib.definitions import logic
from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.impls.types.string_matcher import matcher_options
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.test_resources.strings import WithToString


def negate_matcher(contents_matcher: List[WithToString]) -> List[WithToString]:
    return [logic.NOT_OPERATOR_NAME] + contents_matcher


def matcher_for_expectation_type(expectation_type: ExpectationType,
                                 matcher: List) -> List[WithToString]:
    if expectation_type is ExpectationType.POSITIVE:
        return matcher
    else:
        return negate_matcher(matcher)


def emptiness_matcher() -> List[WithToString]:
    return [file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT]


def equals_matcher(expected) -> List[WithToString]:
    return [matcher_options.EQUALS_ARGUMENT, expected]
