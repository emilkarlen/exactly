from typing import List, Optional

from exactly_lib.definitions.cross_ref.concrete_cross_refs import TestSuiteSectionCrossReference
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.help.program_modes.common import contents as common_contents
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, \
    SectionDocumentation
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text


class TestSuiteSectionDocumentation(SectionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)
        self._section_name = SectionName(name)

    def contents_description(self) -> List[ParagraphItem]:
        raise NotImplementedError()

    def instructions_section_header(self) -> Text:
        return common_contents.INSTRUCTIONS_SECTION_HEADER

    @property
    def syntax_name_cross_ref_text(self) -> docs.Text:
        return docs.cross_reference(self.syntax_name_text,
                                    TestSuiteSectionCrossReference(self.name.plain),
                                    allow_rendering_of_visible_extra_target_text=False)


class TestSuiteSectionDocumentationForSectionWithInstructions(TestSuiteSectionDocumentation):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        """
        :param instruction_set: None if this phase does not have instructions.
        """
        super().__init__(name)
        self._instruction_set = instruction_set

    @property
    def has_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> Optional[SectionInstructionSet]:
        return self._instruction_set

    def contents_description(self) -> List[ParagraphItem]:
        return [docs.para('Consists of zero or more instructions.')] + self.instruction_purpose_description()

    def instruction_purpose_description(self) -> List[ParagraphItem]:
        raise NotImplementedError()


class TestSuiteSectionDocumentationBaseForSectionWithoutInstructions(TestSuiteSectionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    def has_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> SectionInstructionSet:
        return None
