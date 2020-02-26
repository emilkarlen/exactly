from typing import Callable, Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_case_utils.files_condition.test_resources.arguments_building import FilesCondition
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import FilesMatcherArg


def contains_and_equals_cases() -> Sequence[NameAndValue[Callable[[FilesCondition], FilesMatcherArg]]]:
    return _CASES


_CASES = [
    NameAndValue(
        'contains',
        args.Contains,
    ),
    NameAndValue(
        'equals',
        args.Equals,
    ),
]
