import enum
from typing import Dict, Sequence, Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.util import line_source


class Instruction:
    """
    Base class for an element of a section that is something to be "executed"
    - e.g. not empty space or comments.
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
                description: Optional[str] = None,
                ):
        return tuple.__new__(cls, (instruction, description))

    @property
    def instruction(self) -> Instruction:
        return self[0]

    @property
    def description(self) -> Optional[str]:
        return self[1]


class SectionContentElement:
    """
    Element of the contents of a section: either a comment or an instruction.

    Construct elements with either new_comment_element or new_instruction_element.
    """

    def __init__(self,
                 element_type: ElementType,
                 instruction_info: InstructionInfo,
                 source_location_info: SourceLocationInfo):
        self._element_type = element_type
        self._instruction_info = instruction_info
        self._source_location_info = source_location_info

    @property
    def element_type(self) -> ElementType:
        return self._element_type

    @property
    def source_location_info(self) -> SourceLocationInfo:
        return self._source_location_info

    @property
    def source(self) -> line_source.LineSequence:
        """
        :return: Short cut to the source component of `source_location_info`
        """
        return self.source_location_info.source_location_path.location.source

    @property
    def instruction_info(self) -> InstructionInfo:
        """
        Precondition: Element type is INSTRUCTION.
        """
        return self._instruction_info


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

    def elements_for_section_or_empty_if_phase_not_present(self, section_name: str) -> SectionContents:
        if section_name in self._section2elements:
            return self.elements_for_section(section_name)
        else:
            return SectionContents(())


def empty_document() -> Document:
    return Document({})
