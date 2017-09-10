import re

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.named_element.symbol.string_resolver import StringResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime, \
    from_parse_source
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.util.string import lines_content

DOCUMENT_MARKER_PREFIX = '<<'
DOCUMENT_TOKEN_RE = re.compile('(<<)([0-9a-zA-Z_-]+)')


class HereDocumentContentsParsingException(SingleInstructionInvalidArgumentException):
    def __init__(self, error_message: str):
        super().__init__(error_message)


def parse_as_last_argument(here_document_is_mandatory: bool,
                           source: ParseSource) -> StringResolver:
    """
    Expects the here-document marker to be the ane and only token remaining on the current line.
    Consumes current line and all lines included in the here-document.
    :param source: Has a current line, and the remaining part of the current line is expected
    to be the here-document marker.
    :return: list of lines in the here-document, None if doc is not mandatory and not present
    """
    with from_parse_source(source,
                           consume_last_line_if_is_at_eol_after_parse=True) as token_parser:
        return parse_as_last_argument_from_token_parser(here_document_is_mandatory, token_parser)


def parse_as_last_argument_from_token_parser(here_document_is_mandatory: bool,
                                             token_parser: TokenParserPrime) -> StringResolver:
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

    if token_parser.is_at_eol:
        if here_document_is_mandatory:
            raise SingleInstructionInvalidArgumentException(instruction_arguments.HERE_DOCUMENT.name)
        else:
            token_parser.consume_current_line_as_plain_string()
            return None

    first_token = token_parser.token_stream.head
    if first_token.is_quoted:
        return raise_not_a_here_doc_exception()
    marker_match = re.fullmatch(DOCUMENT_TOKEN_RE, first_token.source_string)
    if not marker_match:
        return raise_not_a_here_doc_exception()
    token_parser.consume_mandatory_token('impl: will succeed since because of check above')
    token_parser.report_superfluous_arguments_if_not_at_eol()

    marker = marker_match.group(2)

    token_parser.consume_current_line_as_plain_string()
    return _parse_document_lines_from_token_parser(marker, token_parser)


def _parse_document_lines(marker: str, source: ParseSource) -> StringResolver:
    here_doc = []
    source.consume_current_line()
    while source.has_current_line:
        line = source.current_line_text
        source.consume_current_line()
        if line == marker:
            return _resolver_from_lines(here_doc)
        here_doc.append(line)
    raise HereDocumentContentsParsingException("End Of File reached without finding Marker: '{}'".format(marker))


def _parse_document_lines_from_token_parser(marker: str, token_parser: TokenParserPrime) -> StringResolver:
    here_doc = []
    while token_parser.has_current_line:
        line = token_parser.consume_current_line_as_plain_string()
        if line == marker:
            return _resolver_from_lines(here_doc)
        here_doc.append(line)
    raise HereDocumentContentsParsingException("End Of File reached without finding Marker: '{}'".format(marker))


def _resolver_from_lines(lines: list) -> StringResolver:
    lines_string = lines_content(lines)
    return parse_string.string_resolver_from_string(lines_string)
