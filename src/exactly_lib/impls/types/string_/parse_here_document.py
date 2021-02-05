import re
from typing import Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import string
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.section_document import defs
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, \
    from_parse_source
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.util.parse.token import TokenMatcher, Token
from exactly_lib.util.str_.misc_formatting import lines_content


class HereDocArgTokenMatcher(TokenMatcher):
    def matches(self, token: Token) -> bool:
        return (
                token.is_plain and
                token.string.startswith(string.HERE_DOCUMENT_MARKER_PREFIX)
        )


class HereDocumentContentsParsingException(SingleInstructionInvalidArgumentException):
    def __init__(self, error_message: str):
        super().__init__(error_message)


def parse_as_last_argument(here_document_is_mandatory: bool,
                           source: ParseSource) -> StringSdv:
    """
    Expects the here-document marker to be the ane and only token remaining on the current line.
    Consumes current line and all lines included in the here-document.
    :param source: Has a current line, and the remaining part of the current line is expected
    to be the here-document marker.
    :return: list of lines in the here-document, None if doc is not mandatory and not present
    """
    with from_parse_source(source) as token_parser:
        ret_val = parse_as_last_argument_from_token_parser(here_document_is_mandatory, token_parser)
    if source.is_at_eol:
        source.consume_current_line()
    return ret_val


def parse_as_last_argument_from_token_parser__mandatory(token_parser: TokenParser,
                                                        consume_last_line: bool = True) -> StringSdv:
    return parse_as_last_argument_from_token_parser(True, token_parser, consume_last_line)


def parse_as_last_argument_from_token_parser(here_document_is_mandatory: bool,
                                             token_parser: TokenParser,
                                             consume_last_line: bool = True) -> Optional[StringSdv]:
    """
    Expects the here-document marker to be the ane and only token remaining on the current line.
    Consumes current line and all lines included in the here-document.
    :param token_parser: Has a current line, and the remaining part of the current line is expected
    to be the here-document marker.
    :return: list of lines in the here-document, None if doc is not mandatory and not present
    """

    if not here_document_is_mandatory and token_parser.is_at_eol:
        token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
        return None

    token_parser.require_has_valid_head_token(syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT.singular_name)

    first_token = token_parser.token_stream.head
    if first_token.is_quoted:
        return _raise_not_a_here_doc_exception(token_parser.remaining_part_of_current_line)
    start_token = token_parser.consume_mandatory_token('impl: will succeed since because of check above')
    return parse_document_of_start_str(start_token.string, token_parser, consume_last_line)


def _parse_document_lines(marker: str, source: ParseSource) -> StringSdv:
    here_doc = []
    source.consume_current_line()
    while source.has_current_line:
        line = source.current_line_text
        source.consume_current_line()
        if line == marker:
            return _sdv_from_lines(here_doc)
        here_doc.append(line)
    return _raise_end_marker_not_found(marker)


def parse_document_of_start_str(here_doc_start: str,
                                token_parser: TokenParser,
                                consume_last_line: bool,
                                ) -> StringSdv:
    marker_match = re.fullmatch(string.HERE_DOCUMENT_TOKEN_RE, here_doc_start)
    if not marker_match:
        return _raise_not_a_here_doc_exception(here_doc_start)
    marker = marker_match.group(2)
    token_parser.report_superfluous_arguments_if_not_at_eol()
    token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
    return parse_document_lines_from_token_parser(marker, token_parser, consume_last_line)


def parse_document_lines_from_token_parser(marker: str,
                                           token_parser: TokenParser,
                                           consume_last_line: bool) -> StringSdv:
    here_doc = []
    while token_parser.has_current_line:
        line = token_parser.consume_remaining_part_of_current_line_as_string()
        if line == marker:
            if consume_last_line:
                token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
            return _sdv_from_lines(here_doc)
        here_doc.append(line)
        token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
    return _raise_end_marker_not_found(marker)


def _sdv_from_lines(lines: list) -> StringSdv:
    lines_string = lines_content(lines)
    return parse_string.string_sdv_from_string(lines_string)


def _raise_not_a_here_doc_exception(source: str) -> StringSdv:
    raise SingleInstructionInvalidArgumentException('Not a {}: {}'.format(
        syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT.singular_name,
        source))


def _raise_end_marker_not_found(marker: str) -> StringSdv:
    raise HereDocumentContentsParsingException(
        "{eof} reached without finding Marker: '{m}'".format(
            eof=defs.END_OF_FILE,
            m=marker,
        )
    )
