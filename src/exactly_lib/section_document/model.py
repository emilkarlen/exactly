import enum
import pathlib
from typing import Dict, Sequence

from exactly_lib.util import line_source
from exactly_lib.util.line_source import SourceLocation, SourceLocationPath


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
                 source: line_source.LineSequence,
                 instruction_info: InstructionInfo,
                 file_path: pathlib.Path = None,
                 file_inclusion_chain: Sequence[SourceLocation] = (),
                 abs_path_of_dir_containing_file: pathlib.Path = None):
        self._element_type = element_type
        self._source = source
        self._instruction_info = instruction_info
        self._location = SourceLocation(source, file_path)
        self._file_inclusion_chain = file_inclusion_chain
        self._abs_path_of_dir_containing_file = abs_path_of_dir_containing_file

    @property
    def location(self) -> SourceLocation:
        """
        Gives the
         - source code of the element
         - file path that contains the element (or None iff the element is not from a file (but from stdin, i.e.)
           file path is relative the location of the last element in file_inclusion_chain
           If there is no file_inclusion_chain element, then it is the (relative) path of the root file
        """
        return self._location

    @property
    def file_inclusion_chain(self) -> Sequence[SourceLocation]:
        """
        Each element holds
         - the source code that "represents" the inclusion directive
         - the file that contains the above source code.
           the file path is relative the location of the file of the previous inclusion chain element

        :return: The sequence of file inclusions that leads to the file specified by `location`.
        """
        return self._file_inclusion_chain

    @property
    def source_location_path(self) -> SourceLocationPath:
        return SourceLocationPath(self.location,
                                  self.file_inclusion_chain)

    @property
    def file_path(self) -> pathlib.Path:
        """
        :return: The file component of `location`
        """
        return self._location.file_path

    @property
    def abs_path_of_dir_containing_file(self) -> pathlib.Path:
        """
        :return: The absolute path of the dir that contains
        the final component of `file_path`,
        or, if `file_path` is None, a path that
        serves the same purpose for specifying paths
        relative to (the base name of) `file_path`.

        I.e., the absolute path of `file_path` is

          self.abs_path_of_dir_containing_file / self.file_path.name
        """
        return self._abs_path_of_dir_containing_file

    @property
    def source(self) -> line_source.LineSequence:
        """
        :return: The source component of `location`
        """
        return self._source

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
