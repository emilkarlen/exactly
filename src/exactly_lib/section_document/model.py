import enum
from pathlib import Path
from typing import Dict, Sequence, Optional

from exactly_lib.section_document.source_location import SourceLocationPath
from exactly_lib.util import line_source


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
                description: str = None):
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
                 instruction_info: InstructionInfo,
                 abs_path_of_dir_containing_root_file: Path,
                 source_location_path: SourceLocationPath,
                 abs_path_of_dir_containing_file: Path = None):
        self._element_type = element_type
        self._instruction_info = instruction_info
        self._abs_path_of_dir_containing_root_file = abs_path_of_dir_containing_root_file
        self._source_location_path = source_location_path
        self._abs_path_of_dir_containing_file = abs_path_of_dir_containing_file

    @property
    def abs_path_of_dir_containing_root_file(self) -> Path:
        return self._abs_path_of_dir_containing_root_file

    @property
    def source_location_path(self) -> SourceLocationPath:
        return self._source_location_path

    @property
    def abs_path_of_dir_containing_file(self) -> Optional[Path]:
        """
        :return: The absolute path of the dir that contains
        the final component of `file_path_rel_referrer`,
        or, if `file_path_rel_referrer` is None, a path that
        serves the same purpose for specifying paths
        relative to (the base name of) `file_path_rel_referrer`.

        I.e., the absolute path of `file_path_rel_referrer` is

          self.abs_path_of_dir_containing_file / self.file_path_rel_referrer.name
        """
        return self._abs_path_of_dir_containing_file

    @property
    def source(self) -> line_source.LineSequence:
        """
        :return: Short cut to the source component of `source_location_path.location`
        """
        return self.source_location_path.location.source

    @property
    def element_type(self) -> ElementType:
        return self._element_type

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

    def elements_for_section_or_empty_if_phase_not_present(self, phase_name: str) -> SectionContents:
        if phase_name in self._section2elements:
            return self.elements_for_section(phase_name)
        else:
            return SectionContents(())


def empty_document() -> Document:
    return Document({})
