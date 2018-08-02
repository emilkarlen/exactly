import pathlib
from typing import Sequence, Optional

from exactly_lib.section_document.model import SectionContentElement, ElementType, Instruction, InstructionInfo
from exactly_lib.util import line_source
from exactly_lib.util.line_source import SourceLocationPath, SourceLocation, LineSequence


class SourceLocationInfo:
    def __init__(self,
                 file_path_rel_referrer: Optional[pathlib.Path] = None,
                 file_inclusion_chain: Sequence[line_source.SourceLocation] = (),
                 abs_path_of_dir_containing_file: Optional[pathlib.Path] = None,
                 ):
        self._file_path_rel_referrer = file_path_rel_referrer
        self._file_inclusion_chain = file_inclusion_chain
        self._abs_path_of_dir_containing_file = abs_path_of_dir_containing_file

    def source_location_of(self, source: LineSequence) -> SourceLocation:
        return SourceLocation(source, self._file_path_rel_referrer)

    def source_location_path(self, source: LineSequence) -> SourceLocationPath:
        return SourceLocationPath(self.source_location_of(source),
                                  self._file_inclusion_chain)

    def location_path_of(self, source: LineSequence) -> Sequence[SourceLocation]:
        return list(self._file_inclusion_chain) + [self.source_location_of(source)]

    @property
    def abs_path_of_dir_containing_file(self) -> Optional[pathlib.Path]:
        return self._abs_path_of_dir_containing_file


class SectionContentElementBuilder:
    """Build SectionContentElement:s"""

    def __init__(self, source_location_builder: SourceLocationInfo):
        self._loc_builder = source_location_builder

    def new_empty(self, source: LineSequence) -> SectionContentElement:
        return self.new_non_instruction(source,
                                        ElementType.EMPTY)

    def new_comment(self, source: LineSequence) -> SectionContentElement:
        return self.new_non_instruction(source,
                                        ElementType.COMMENT)

    def new_non_instruction(self,
                            source: LineSequence,
                            element_type: ElementType) -> SectionContentElement:
        return self._new(element_type,
                         source,
                         None)

    def new_instruction(self,
                        source: LineSequence,
                        instruction: Instruction,
                        description: str = None) -> SectionContentElement:
        return self._new(ElementType.INSTRUCTION,
                         source,
                         InstructionInfo(instruction,
                                         description))

    def _new(self,
             element_type: ElementType,
             source: LineSequence,
             instruction_info: Optional[InstructionInfo]) -> SectionContentElement:
        return SectionContentElement(element_type,
                                     instruction_info,
                                     self._loc_builder.source_location_path(source),
                                     self._loc_builder.abs_path_of_dir_containing_file)

    def location_path_of(self, source: LineSequence) -> Sequence[line_source.SourceLocation]:
        return self._loc_builder.location_path_of(source)
