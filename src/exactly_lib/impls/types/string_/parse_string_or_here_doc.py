from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import string
from exactly_lib.impls.types.string_ import parse_string, parse_here_document
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, \
    from_parse_source
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv

_SYNTAX_ELEMENT_NAME = '|'.join([
    syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
    syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT.singular_name,
])


def parse_string_or_here_doc_from_parse_source(source: ParseSource,
                                               consume_last_here_doc_line: bool = True,
                                               ) -> StringSdv:
    with from_parse_source(source,
                           consume_last_line_if_is_at_eol_after_parse=False) as token_parser:
        return parse_string_or_here_doc_from_token_parser(token_parser, consume_last_here_doc_line)


def parse_string_or_here_doc_from_token_parser(token_parser: TokenParser,
                                               consume_last_here_doc_line: bool = True
                                               ) -> StringSdv:
    token_parser.require_has_valid_head_token(_SYNTAX_ELEMENT_NAME)
    if token_parser.token_stream.head.source_string.startswith(string.HERE_DOCUMENT_MARKER_PREFIX):
        return parse_here_document.parse_as_last_argument_from_token_parser(True, token_parser,
                                                                            consume_last_here_doc_line)
    else:
        return parse_string.parse_string_from_token_parser(token_parser)
