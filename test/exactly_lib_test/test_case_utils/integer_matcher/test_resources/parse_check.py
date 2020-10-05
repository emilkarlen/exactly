from typing import Sequence

from exactly_lib.test_case_utils.integer_matcher import parse_integer_matcher
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_case_utils.test_resources.parse_checker import Checker
from exactly_lib_test.test_case_utils.test_resources.parse_checker import parse_checker

PARSE_CHECKER__FULL = parse_checker(parse_integer_matcher.parsers().full)

PARSE_CHECKER__SIMPLE = parse_checker(parse_integer_matcher.parsers().simple)


def _parser_checkers__for_type_hints() -> Sequence[NameAndValue[Checker]]:
    return [
        NameAndValue(
            'simple',
            PARSE_CHECKER__SIMPLE,
        ),
        NameAndValue(
            'full',
            PARSE_CHECKER__FULL,
        ),
    ]


PARSE_CHECKERS = _parser_checkers__for_type_hints()
