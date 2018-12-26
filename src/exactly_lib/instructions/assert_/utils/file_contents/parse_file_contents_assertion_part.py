from exactly_lib.instructions.assert_.utils import assertion_part
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.parts.contents_checkers import FileTransformerAsAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.string_matcher_assertion_part import \
    StringMatcherAssertionPart
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.string_matcher.parse import parse_string_matcher
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer


def parse(token_parser: TokenParser) -> AssertionPart:
    """
    :return: A :class:`AssertionPart` that takes an ResolvedComparisonActualFile as (last) argument.
    """

    actual_lines_transformer = parse_string_transformer.parse_optional_transformer_resolver_preceding_mandatory_element(
        token_parser,
        parse_string_matcher.COMPARISON_OPERATOR,
    )
    string_matcher_resolver = parse_string_matcher.parse_string_matcher(token_parser)
    file_contents_assertion_part = StringMatcherAssertionPart(string_matcher_resolver)
    return assertion_part.compose(FileTransformerAsAssertionPart(actual_lines_transformer),
                                  file_contents_assertion_part)
