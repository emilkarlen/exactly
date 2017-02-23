from exactly_lib.section_document import model
from exactly_lib.section_document import new_parser_classes as parse2
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
                                           SourceCodeInstruction(line_sequence), None)


# TODO [instr-desc] Rename when new parser structures are fully integrated
class PlainSourceActPhaseParser2(parse2.SectionElementParser2):
    def parse(self, source: parse2.ParseSource) -> model.SectionContentElement:
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
        return model.SectionContentElement(model.ElementType.INSTRUCTION,
                                           line_sequence,
                                           SourceCodeInstruction(line_sequence), None)

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
                                           SourceCodeInstruction(line_sequence), None)


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
