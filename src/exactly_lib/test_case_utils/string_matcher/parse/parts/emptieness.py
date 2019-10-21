from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.test_case_utils.string_matcher.emptiness_matcher import EmptinessStringMatcherValue
from exactly_lib.test_case_utils.string_matcher.resolvers import StringMatcherConstantOfValueResolver
from exactly_lib.util.logic_types import ExpectationType


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherResolver:
    return value_resolver(expectation_type)


def value_resolver(expectation_type: ExpectationType) -> StringMatcherResolver:
    return StringMatcherConstantOfValueResolver(
        EmptinessStringMatcherValue(expectation_type)
    )
