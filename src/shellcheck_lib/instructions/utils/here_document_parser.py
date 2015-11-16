import re

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException

DOCUMENT_TOKEN_RE = re.compile('(<<)([0-9a-zA-Z_-]+)')


def parse_as_last_argument(here_document_is_mandatory: bool,
                           first_line_arguments: list,
                           source: SingleInstructionParserSource) -> list:
    if not first_line_arguments:
        if here_document_is_mandatory:
            raise SingleInstructionInvalidArgumentException('Missing here-document')
        return []
    first_argument = first_line_arguments[0]
    marker_match = re.fullmatch(DOCUMENT_TOKEN_RE, first_argument)
    if not marker_match:
        raise SingleInstructionInvalidArgumentException('Not a Here Document token: {}'.format(first_argument))
    if len(first_line_arguments) > 1:
        raise SingleInstructionInvalidArgumentException('Superfluous arguments: {}'.format(first_line_arguments[1:]))
    marker = marker_match.group(2)
    ret_val = []
    line_sequence = source.line_sequence
    while line_sequence.has_next():
        line = line_sequence.next_line()
        if line == marker:
            return ret_val
        ret_val.append(line)
    raise SingleInstructionInvalidArgumentException('End Of File reached without finding Marker: {}'.format(marker))
