import enum
import pathlib
from typing import Dict, Sequence

from exactly_lib.util import line_source
from exactly_lib.util.line_source import LineInFile, SourceLocation


class Instruction:
    """
    Base class for an element of a phase that is not a comment.
    """
    pass


class ElementType(enum.Enum):
    EMPTY = 1
    COMMENT = 2
    INSTRUCTION = 3


class InstructionInfo(tuple):
    """
    Information about an instruction in a SectionContentElement.
    """

    def __new__(cls,
                instruction: Instruction,
                description: str):
        return tuple.__new__(cls, (instruction, description))

    @property
    def instruction(self) -> Instruction:
        return self[0]

    @property
    def description(self) -> str:
        return self[1]


class SectionContentElement:
    """
    Element of the contents of a section: either a comment or an instruction.

    Construct elements with either new_comment_element or new_instruction_element.
    """

    def __init__(self,
                 element_type: ElementType,
                 source: line_source.LineSequence,
                 instruction_info: InstructionInfo,
                 file_path: pathlib.Path = None):
        self._element_type = element_type
        self._source = source
        self._instruction_info = instruction_info
        self._location = SourceLocation(source, file_path)

    @property
    def location(self) -> SourceLocation:
        return self._location

    @property
    def location_as_line_in_file(self) -> LineInFile:
        return LineInFile(self._location.source.first_line,
                          self._location.file_path)

    @property
    def source(self) -> line_source.LineSequence:
        return self._source

    @property
    def first_line(self) -> line_source.Line:
        return self._source.first_line

    @property
    def element_type(self) -> ElementType:
        return self._element_type

    @property
    def instruction_info(self) -> InstructionInfo:
        """
        Precondition: Element type is INSTRUCTION.
        """
        return self._instruction_info


class SectionContentElementBuilder:
    def __init__(self, file_path: pathlib.Path = None):
        self._file_path = file_path

    def new_empty(self, source: line_source.LineSequence) -> SectionContentElement:
        return SectionContentElement(ElementType.EMPTY,
                                     source,
                                     None,
                                     self._file_path)

    def new_comment(self, source: line_source.LineSequence) -> SectionContentElement:
        return SectionContentElement(ElementType.COMMENT,
                                     source,
                                     None,
                                     self._file_path)

    def new_instruction(self,
                        source: line_source.LineSequence,
                        instruction: Instruction,
                        description: str = None) -> SectionContentElement:
        return SectionContentElement(ElementType.INSTRUCTION,
                                     source,
                                     InstructionInfo(instruction,
                                                     description),
                                     self._file_path)


class SectionContents:
    """
    The SectionContentElement:s of a single section.
    """

    def __init__(self, elements: Sequence[SectionContentElement]):
        self._elements = elements

    @property
    def elements(self) -> Sequence[SectionContentElement]:
        return self._elements


def new_empty_section_contents() -> SectionContents:
    return SectionContents(())


class Document:
    """
    The result of parsing a file without encountering any errors.
    """

    def __init__(self, section2elements: Dict[str, SectionContents]):
        self._section2elements = section2elements

    @property
    def section(self) -> frozenset:
        return frozenset(self._section2elements.keys())

    @property
    def section_2_elements(self) -> Dict[str, SectionContents]:
        return self._section2elements

    def elements_for_section(self, section_name: str) -> SectionContents:
        return self._section2elements[section_name]

    def elements_for_section_or_empty_if_phase_not_present(self, phase_name: str) -> SectionContents:
        if phase_name in self._section2elements:
            return self.elements_for_section(phase_name)
        else:
            return SectionContents(())


def empty_document() -> Document:
    return Document({})
