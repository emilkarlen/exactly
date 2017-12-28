import pathlib
from typing import Sequence

from exactly_lib.section_document.model import SectionContentElement, ElementType, Instruction, InstructionInfo
from exactly_lib.util import line_source


class SectionContentElementBuilder:
    """Build SectionContentElement:s"""

    def __init__(self,
                 file_path: pathlib.Path = None,
                 file_inclusion_chain: Sequence[line_source.SourceLocation] = ()):
        self._file_path = file_path
        self._file_inclusion_chain = file_inclusion_chain

    def new_empty(self, source: line_source.LineSequence) -> SectionContentElement:
        return SectionContentElement(ElementType.EMPTY,
                                     source,
                                     None,
                                     self._file_path,
                                     self._file_inclusion_chain)

    def new_comment(self, source: line_source.LineSequence) -> SectionContentElement:
        return SectionContentElement(ElementType.COMMENT,
                                     source,
                                     None,
                                     self._file_path,
                                     self._file_inclusion_chain)

    def new_instruction(self,
                        source: line_source.LineSequence,
                        instruction: Instruction,
                        description: str = None) -> SectionContentElement:
        return SectionContentElement(ElementType.INSTRUCTION,
                                     source,
                                     InstructionInfo(instruction,
                                                     description),
                                     self._file_path,
                                     self._file_inclusion_chain)
