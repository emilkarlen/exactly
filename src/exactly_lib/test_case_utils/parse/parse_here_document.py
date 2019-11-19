import re
from typing import Optional

from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, \
    from_parse_source
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.util.string import lines_content

DOCUMENT_MARKER_PREFIX = '<<'
DOCUMENT_TOKEN_RE = re.compile('(<<)([0-9a-zA-Z_-]+)')


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

    def raise_not_a_here_doc_exception():
        raise SingleInstructionInvalidArgumentException('Not a {}: {}'.format(
            instruction_arguments.HERE_DOCUMENT.name,
            token_parser.remaining_part_of_current_line))

    if not here_document_is_mandatory and token_parser.is_at_eol:
        token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
        return None

    token_parser.require_has_valid_head_token(instruction_arguments.HERE_DOCUMENT.name)

    while token_parser.is_at_eol:
        token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()

    first_token = token_parser.token_stream.head
    if first_token.is_quoted:
        return raise_not_a_here_doc_exception()
    marker_match = re.fullmatch(DOCUMENT_TOKEN_RE, first_token.source_string)
    if not marker_match:
        return raise_not_a_here_doc_exception()
    token_parser.consume_mandatory_token('impl: will succeed since because of check above')
    token_parser.report_superfluous_arguments_if_not_at_eol()

    marker = marker_match.group(2)

    token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
    string_sdv = _parse_document_lines_from_token_parser(marker, token_parser)
    if consume_last_line:
        token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
    return string_sdv


def _parse_document_lines(marker: str, source: ParseSource) -> StringSdv:
    here_doc = []
    source.consume_current_line()
    while source.has_current_line:
        line = source.current_line_text
        source.consume_current_line()
        if line == marker:
            return _sdv_from_lines(here_doc)
        here_doc.append(line)
    raise HereDocumentContentsParsingException("End Of File reached without finding Marker: '{}'".format(marker))


def _parse_document_lines_from_token_parser(marker: str, token_parser: TokenParser) -> StringSdv:
    here_doc = []
    while token_parser.has_current_line:
        line = token_parser.consume_remaining_part_of_current_line_as_string()
        if line == marker:
            return _sdv_from_lines(here_doc)
        here_doc.append(line)
        token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()
    raise HereDocumentContentsParsingException("End Of File reached without finding Marker: '{}'".format(marker))


def _sdv_from_lines(lines: list) -> StringSdv:
    lines_string = lines_content(lines)
    return parse_string.string_sdv_from_string(lines_string)
