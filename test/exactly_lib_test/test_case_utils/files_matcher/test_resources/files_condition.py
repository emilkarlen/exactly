from typing import Callable

from exactly_lib_test.test_case_utils.files_condition.test_resources.arguments_building import FilesCondition
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.files_matcher.test_resources.arguments_building import FilesMatcherArg


class MatcherCase:
    def __init__(self,
                 name: str,
                 arguments_for_fc: Callable[[FilesCondition], FilesMatcherArg],
                 ):
        self.name = name
        self.arguments_for_fc = arguments_for_fc


CONTAINS_AND_EQUALS_CASES = [
    MatcherCase(
        'contains',
        args.Contains,
    ),
    MatcherCase(
        'equals',
        args.Equals,
    ),
]
