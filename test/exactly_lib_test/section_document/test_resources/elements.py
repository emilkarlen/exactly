from exactly_lib.section_document.model import SectionContentElement, ElementType, Instruction
from exactly_lib.util import line_source
from exactly_lib.util.line_source import Line, LineSequence


def new_comment_element(source_line: line_source.Line) -> SectionContentElement:
    return SectionContentElement(ElementType.COMMENT,
                                 new_ls_from_line(source_line),
                                 None, None)


def new_instruction_element(source_line: line_source.Line,
                            instruction: Instruction) -> SectionContentElement:
    return SectionContentElement(ElementType.INSTRUCTION,
                                 new_ls_from_line(source_line),
                                 instruction, None)


def new_ls_from_line(line: Line) -> LineSequence:
    return LineSequence(line.line_number,
                        (line.text,))
