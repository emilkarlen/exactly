from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.test_case_utils.string_matcher.emptiness_matcher import EmptinessStringMatcher
from exactly_lib.test_case_utils.string_matcher.resolvers import StringMatcherConstantResolver
from exactly_lib.util.logic_types import ExpectationType


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherResolver:
    token_parser.report_superfluous_arguments_if_not_at_eol()
    token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
    return value_resolver(expectation_type)


def value_resolver(expectation_type: ExpectationType) -> StringMatcherResolver:
    return StringMatcherConstantResolver(
        EmptinessStringMatcher(expectation_type)
    )
