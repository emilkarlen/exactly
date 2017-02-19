import re

from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException

DOCUMENT_TOKEN_RE = re.compile('(<<)([0-9a-zA-Z_-]+)')


class HereDocumentContentsParsingException(SingleInstructionInvalidArgumentException):
    def __init__(self, error_message: str):
        super().__init__(error_message)


def parse_as_last_argumentInstrDesc(here_document_is_mandatory: bool,
                                    source: ParseSource) -> list:
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
            raise SingleInstructionInvalidArgumentException('Missing here-document')
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
    here_doc = []
    source.consume_current_line()
    while source.has_current_line:
        line = source.current_line_text
        source.consume_current_line()
        if line == marker:
            return here_doc
        here_doc.append(line)
    raise HereDocumentContentsParsingException("End Of File reached without finding Marker: '{}'".format(marker))


# TODO [instr-desc] Remove when new parser structures are fully integrated
def parse(first_line_arguments: list,
          source: SingleInstructionParserSource) -> (list, list):
    if not first_line_arguments:
        raise SingleInstructionInvalidArgumentException('Missing here-document')
    first_argument = first_line_arguments[0]
    marker_match = re.fullmatch(DOCUMENT_TOKEN_RE, first_argument)
    if not marker_match:
        raise SingleInstructionInvalidArgumentException('Not a Here Document token: {}'.format(first_argument))
    marker = marker_match.group(2)
    here_doc = []
    line_sequence = source.line_sequence
    while line_sequence.has_next():
        line = line_sequence.next_line()
        if line == marker:
            return here_doc, first_line_arguments[1:]
        here_doc.append(line)
    raise HereDocumentContentsParsingException("End Of File reached without finding Marker: '{}'".format(marker))


def parse_as_last_argument(here_document_is_mandatory: bool,
                           first_line_arguments: list,
                           source: SingleInstructionParserSource) -> list:
    try:
        (here_doc, remaining_arguments) = parse(first_line_arguments, source)
        if remaining_arguments:
            raise SingleInstructionInvalidArgumentException('Superfluous arguments: {}'.format(remaining_arguments))
        return here_doc
    except HereDocumentContentsParsingException as ex:
        raise ex
    except SingleInstructionInvalidArgumentException:
        if here_document_is_mandatory:
            raise SingleInstructionInvalidArgumentException('Missing here-document')
        if first_line_arguments:
            raise SingleInstructionInvalidArgumentException('Superfluous arguments: {}'.format(first_line_arguments))
        return []
