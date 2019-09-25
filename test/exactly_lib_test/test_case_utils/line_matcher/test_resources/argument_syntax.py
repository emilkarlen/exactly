import exactly_lib.definitions.primitives.line_matcher
from exactly_lib.definitions import expression
from exactly_lib.test_case_utils.condition import comparators


def syntax_for_regex_matcher(regex_token_str: str) -> str:
    return ' '.join([
        exactly_lib.definitions.primitives.line_matcher.REGEX_MATCHER_NAME,
        regex_token_str,
    ])


def syntax_for_line_number_matcher(comparator: comparators.ComparisonOperator,
                                   integer_argument: str) -> str:
    return ' '.join([
        exactly_lib.definitions.primitives.line_matcher.LINE_NUMBER_MATCHER_NAME,
        comparator.name,
        integer_argument
    ])


def syntax_for_and(matchers: list) -> str:
    return (' ' + expression.AND_OPERATOR_NAME + ' ').join(matchers)


def syntax_for_arbitrary_line_matcher() -> str:
    return syntax_for_regex_matcher('matches')
