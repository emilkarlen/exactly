from exactly_lib.section_document.model import PhaseContentElement, ElementType, Instruction
from exactly_lib.util import line_source
from exactly_lib.util.line_source import Line, LineSequence


def new_comment_element(source_line: line_source.Line) -> PhaseContentElement:
    return PhaseContentElement(ElementType.COMMENT,
                               new_ls_from_line(source_line),
                               None)


def new_instruction_element(source_line: line_source.Line,
                            instruction: Instruction) -> PhaseContentElement:
    return PhaseContentElement(ElementType.INSTRUCTION,
                               new_ls_from_line(source_line),
                               instruction)


def new_ls_from_line(line: Line) -> LineSequence:
    return LineSequence(line.line_number,
                        (line.text,))
