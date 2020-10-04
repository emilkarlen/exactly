from exactly_lib.definitions import logic
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib_test.test_case_utils.line_matcher.test_resources import arguments_building as lm_args
from exactly_lib_test.test_case_utils.string_matcher.test_resources import arguments_building2 as sm_args


def syntax_for_regex_matcher(regex_token_str: str) -> str:
    return lm_args.Contents(sm_args.Matches(regex_token_str)).as_str


def syntax_for_line_number_matcher(comparator: comparators.ComparisonOperator,
                                   integer_argument: str) -> str:
    return ' '.join([
        line_matcher.LINE_NUMBER_MATCHER_NAME,
        comparator.name,
        integer_argument
    ])


def syntax_for_and(matchers: list) -> str:
    return (' ' + logic.AND_OPERATOR_NAME + ' ').join(matchers)


def syntax_for_arbitrary_line_matcher() -> str:
    return syntax_for_regex_matcher('matches')
