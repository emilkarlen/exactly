from exactly_lib.section_document import model
from exactly_lib.section_document import parse
from exactly_lib.section_document import syntax
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.util import line_source
from exactly_lib.util.line_source import LineSequence


class PlainSourceActPhaseParser(parse.SectionElementParser):
    def apply(self, source: line_source.LineSequenceBuilder) -> model.SectionContentElement:
        lines_read = []
        lines_read.append(_un_escape(source.first_line.text))
        while source.has_next():
            next_line = source.next_line()
            if syntax.is_section_header_line(next_line):
                source.return_line()
                break
            lines_read.append(_un_escape(next_line))
        line_sequence = LineSequence(source.first_line.line_number,
                                     tuple(lines_read))
        return model.SectionContentElement(model.ElementType.INSTRUCTION,
                                           line_sequence,
                                           SourceCodeInstruction(line_sequence))


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
    while s[non_space_char_idx].isspace():
        non_space_char_idx += 1
    return s[:non_space_char_idx], s[non_space_char_idx:]


class SourceCodeInstruction(ActPhaseInstruction):
    def __init__(self,
                 source_code: LineSequence):
        self._source_code = source_code

    def source_code(self) -> LineSequence:
        return self._source_code
