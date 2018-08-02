from pathlib import Path
from typing import Sequence, Generic, TypeVar

from exactly_lib.section_document.model import InstructionInfo, ElementType
from exactly_lib.util import line_source


class ParsedSectionElement:
    """The result of applying a SectionElementParser"""

    def __init__(self, source: line_source.LineSequence):
        self._source = source

    @property
    def source(self) -> line_source.LineSequence:
        return self._source


class ParsedInstruction(ParsedSectionElement):
    def __init__(self,
                 source: line_source.LineSequence,
                 instruction_info: InstructionInfo):
        super().__init__(source)
        self._instruction_info = instruction_info

    @property
    def instruction_info(self) -> InstructionInfo:
        return self._instruction_info


class ParsedNonInstructionElement(ParsedSectionElement):
    def __init__(self,
                 source: line_source.LineSequence,
                 element_type: ElementType):
        super().__init__(source)
        self._element_type = element_type

    @property
    def element_type(self) -> ElementType:
        return self._element_type


def new_empty_element(source: line_source.LineSequence) -> ParsedNonInstructionElement:
    return ParsedNonInstructionElement(source, ElementType.EMPTY)


def new_comment_element(source: line_source.LineSequence) -> ParsedNonInstructionElement:
    return ParsedNonInstructionElement(source, ElementType.COMMENT)


class ParsedFileInclusionDirective(ParsedSectionElement):
    def __init__(self,
                 source: line_source.LineSequence,
                 files_to_include: Sequence[Path]):
        super().__init__(source)
        self._files_to_include = files_to_include

    @property
    def files_to_include(self) -> Sequence[Path]:
        return self._files_to_include


T = TypeVar('T')


class ParsedSectionElementVisitor(Generic[T]):
    def visit(self, element: ParsedSectionElement) -> T:
        """
        :return: Return value from _visit... method
        """
        if isinstance(element, ParsedInstruction):
            return self.visit_instruction_element(element)
        elif isinstance(element, ParsedNonInstructionElement):
            return self.visit_non_instruction_element(element)
        elif isinstance(element, ParsedFileInclusionDirective):
            return self.visit_file_inclusion_directive(element)
        else:
            raise TypeError('Unknown {}: {}'.format(ParsedInstruction, str(element)))

    def visit_instruction_element(self, instruction: ParsedInstruction) -> T:
        raise NotImplementedError()

    def visit_non_instruction_element(self, non_instruction: ParsedNonInstructionElement) -> T:
        raise NotImplementedError()

    def visit_file_inclusion_directive(self, file_inclusion: ParsedFileInclusionDirective) -> T:
        raise NotImplementedError()
