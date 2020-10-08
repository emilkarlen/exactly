from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.parse import parse_string
from ..symbol.data.string_sdv import StringSdv


def parse(token_parser: TokenParser) -> StringSdv:
    token_parser.require_has_valid_head_token(_GLOB_PATTERN_STRING_CONFIGURATION.argument_name)
    return parse_string.parse_string_from_token_parser(token_parser, _GLOB_PATTERN_STRING_CONFIGURATION)


_GLOB_PATTERN_STRING_CONFIGURATION = parse_string.Configuration(
    syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.singular_name,
    reference_restrictions=None
)