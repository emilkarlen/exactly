import pathlib
from typing import Sequence

from exactly_lib.section_document.model import SectionContentElement, ElementType, Instruction, InstructionInfo
from exactly_lib.util import line_source


class SectionContentElementBuilder:
    """Build SectionContentElement:s"""

    def __init__(self,
                 file_path: pathlib.Path = None,
                 file_inclusion_chain: Sequence[line_source.SourceLocation] = (),
                 abs_path_of_dir_containing_file: pathlib.Path = None,
                 ):
        self._file_path = file_path
        self._file_inclusion_chain = file_inclusion_chain
        self._abs_path_of_dir_containing_file = abs_path_of_dir_containing_file

    def new_empty(self, source: line_source.LineSequence) -> SectionContentElement:
        return self.new_non_instruction(source,
                                        ElementType.EMPTY)

    def new_comment(self, source: line_source.LineSequence) -> SectionContentElement:
        return self.new_non_instruction(source,
                                        ElementType.COMMENT)

    def new_non_instruction(self,
                            source: line_source.LineSequence,
                            element_type: ElementType) -> SectionContentElement:
        return self._new(element_type,
                         source,
                         None)

    def new_instruction(self,
                        source: line_source.LineSequence,
                        instruction: Instruction,
                        description: str = None) -> SectionContentElement:
        return self._new(ElementType.INSTRUCTION,
                         source,
                         InstructionInfo(instruction,
                                         description))

    def _new(self,
             element_type: ElementType,
             source: line_source.LineSequence,
             instruction_info: InstructionInfo) -> SectionContentElement:
        return SectionContentElement(element_type,
                                     source,
                                     instruction_info,
                                     self._file_path,
                                     self._file_inclusion_chain,
                                     self._abs_path_of_dir_containing_file)

    @property
    def file_path(self) -> pathlib.Path:
        return self._file_path

    @property
    def file_inclusion_chain(self) -> Sequence[line_source.SourceLocation]:
        return self._file_inclusion_chain

    def location_path_of(self, source: line_source.LineSequence) -> Sequence[line_source.SourceLocation]:
        return list(self._file_inclusion_chain) + [line_source.SourceLocation(source, self._file_path)]
