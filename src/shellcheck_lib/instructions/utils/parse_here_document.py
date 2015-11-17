import re

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException

DOCUMENT_TOKEN_RE = re.compile('(<<)([0-9a-zA-Z_-]+)')


class HereDocumentContentsParsingException(SingleInstructionInvalidArgumentException):
    def __init__(self, error_message: str):
        super().__init__(error_message)


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
    raise HereDocumentContentsParsingException('End Of File reached without finding Marker: {}'.format(marker))


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
