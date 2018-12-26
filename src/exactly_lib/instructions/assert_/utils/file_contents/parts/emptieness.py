from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileContentsAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.string_matcher_assertion_part import \
    StringMatcherAssertionPart
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.test_case_utils.string_matcher.emptiness_matcher import EmptinessStringMatcher
from exactly_lib.test_case_utils.string_matcher.resolvers import StringMatcherConstantResolver
from exactly_lib.util.logic_types import ExpectationType


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> FileContentsAssertionPart:
    token_parser.report_superfluous_arguments_if_not_at_eol()
    token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
    return _emptiness_via_string_matcher(expectation_type)


def _emptiness_via_string_matcher(expectation_type: ExpectationType) -> FileContentsAssertionPart:
    return StringMatcherAssertionPart(value_resolver(expectation_type))


def value_resolver(expectation_type: ExpectationType) -> StringMatcherResolver:
    return StringMatcherConstantResolver(
        EmptinessStringMatcher(expectation_type)
    )
