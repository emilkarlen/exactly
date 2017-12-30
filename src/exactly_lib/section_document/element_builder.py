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

    def new_non_instruction(self,
                            source: line_source.LineSequence,
                            element_type: ElementType) -> SectionContentElement:
        return SectionContentElement(element_type,
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
                                     self._file_path,
                                     self._file_inclusion_chain)

    @property
    def file_path(self) -> pathlib.Path:
        return self._file_path

    @property
    def file_inclusion_chain(self) -> Sequence[line_source.SourceLocation]:
        return self._file_inclusion_chain

    def location_path_of(self, source: line_source.LineSequence) -> Sequence[line_source.SourceLocation]:
        return list(self._file_inclusion_chain) + [line_source.SourceLocation(source, self._file_path)]

    def for_inclusion(self,
                      source: line_source.LineSequence,
                      file_to_include: pathlib.Path):
        file_inclusion_chain = self.location_path_of(source)
        return SectionContentElementBuilder(file_to_include,
                                            file_inclusion_chain)
