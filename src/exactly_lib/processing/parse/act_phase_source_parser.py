from exactly_lib.section_document import syntax
from exactly_lib.section_document.model import InstructionInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedInstruction
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.util.line_source import LineSequence


class ActPhaseParser(SectionElementParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> ParsedInstruction:
        first_line_number = source.current_line_number
        current_line = source.current_line_text
        lines_read = [_un_escape(current_line)]
        source.consume_current_line()
        while not source.is_at_eof:
            current_line = source.current_line_text
            if syntax.is_section_header_line(current_line):
                break
            else:
                lines_read.append(_un_escape(current_line))
                source.consume_current_line()

        line_sequence = LineSequence(first_line_number,
                                     tuple(lines_read))
        return ParsedInstruction(line_sequence,
                                 InstructionInfo(SourceCodeInstruction(line_sequence), None))


def _un_escape(s: str) -> str:
    if not s:
        return s
    if not s[0].isspace():
        return _un_escape_at_beginning_of_line(s)
    space, non_space = _split_space(s)
    if not non_space:
        return space
    return space + _un_escape_at_beginning_of_line(non_space)


def _un_escape_at_beginning_of_line(s: str) -> str:
    if s[:2] == '\\[':
        return '[' + s[2:]
    if s[:2] == '\\\\':
        return '\\' + s[2:]
    return s


def _split_space(s: str) -> (str, str):
    non_space_char_idx = 0
    while non_space_char_idx < len(s) and s[non_space_char_idx].isspace():
        non_space_char_idx += 1
    return s[:non_space_char_idx], s[non_space_char_idx:]


class SourceCodeInstruction(ActPhaseInstruction):
    def __init__(self,
                 source_code: LineSequence):
        self._source_code = source_code

    def source_code(self) -> LineSequence:
        return self._source_code
