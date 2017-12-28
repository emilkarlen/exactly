from exactly_lib.section_document.element_builder import SectionContentElementBuilder
from exactly_lib.section_document.model import SectionContentElement, Instruction
from exactly_lib.util import line_source
from exactly_lib.util.line_source import Line, LineSequence

_ELEMENT_BUILDER = SectionContentElementBuilder()


def new_comment_element(source_line: line_source.Line) -> SectionContentElement:
    return _ELEMENT_BUILDER.new_comment(new_ls_from_line(source_line))


def new_instruction_element(source_line: line_source.Line,
                            instruction: Instruction) -> SectionContentElement:
    return _ELEMENT_BUILDER.new_instruction(new_ls_from_line(source_line),
                                            instruction,
                                            None)


def new_ls_from_line(line: Line) -> LineSequence:
    return LineSequence(line.line_number,
                        (line.text,))
