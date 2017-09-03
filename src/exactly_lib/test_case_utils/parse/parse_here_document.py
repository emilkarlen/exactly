import re

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.named_element.symbol.string_resolver import StringResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
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
    source.consume_initial_space_on_current_line()
    if source.is_at_eol:
        if here_document_is_mandatory:
            raise SingleInstructionInvalidArgumentException(instruction_arguments.HERE_DOCUMENT.name)
        else:
            source.consume_current_line()
            return None
    first_argument = source.remaining_part_of_current_line.split(maxsplit=1)[0]
    marker_match = re.fullmatch(DOCUMENT_TOKEN_RE, first_argument)
    if not marker_match:
        raise SingleInstructionInvalidArgumentException('Not a Here Document token: {}'.format(first_argument))
    marker = marker_match.group(2)
    source.consume_part_of_current_line(len(first_argument))
    source.consume_initial_space_on_current_line()
    if not source.is_at_eol:
        raise SingleInstructionInvalidArgumentException(
            'Superfluous arguments: ' + source.remaining_part_of_current_line)
    return _parse_document_lines(marker, source)


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


def _resolver_from_lines(lines: list) -> StringResolver:
    lines_string = lines_content(lines)
    return parse_string.string_resolver_from_string(lines_string)
