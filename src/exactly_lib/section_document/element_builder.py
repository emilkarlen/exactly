from typing import Sequence, Optional

from exactly_lib.section_document.model import SectionContentElement, ElementType, Instruction, InstructionInfo
from exactly_lib.section_document.source_location import SourceLocation, FileLocationInfo
from exactly_lib.util.line_source import LineSequence


class SectionContentElementBuilder:
    """Build SectionContentElement:s"""

    def __init__(self, file_location_info: FileLocationInfo):
        self._loc_info = file_location_info

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
                                     self._loc_info.source_location_info_for(source))

    def location_path_of(self, source: LineSequence) -> Sequence[SourceLocation]:
        return self._loc_info.location_path_of(source)
