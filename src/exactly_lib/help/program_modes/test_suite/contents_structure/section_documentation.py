from typing import List, Optional

from exactly_lib.definitions.section_info import SectionInfo
from exactly_lib.definitions.test_suite.section_infos import TestSuiteSectionInfo, \
    TestSuiteSectionWithoutInstructionsInfo
from exactly_lib.help.program_modes.common import contents as common_contents
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, \
    SectionDocumentation
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text


class TestSuiteSectionDocumentation(SectionDocumentation):
    def __init__(self, section_info: SectionInfo):
        self._section_info = section_info

    @property
    def section_info(self) -> SectionInfo:
        return self._section_info

    def contents_description(self) -> docs.SectionContents:
        raise NotImplementedError()

    def instructions_section_header(self) -> Text:
        return common_contents.INSTRUCTIONS_SECTION_HEADER


class TestSuiteSectionDocumentationForSectionWithInstructions(TestSuiteSectionDocumentation):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        """
        :param instruction_set: None if this phase does not have instructions.
        """
        super().__init__(TestSuiteSectionInfo(name))
        self._instruction_set = instruction_set

    @property
    def has_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> Optional[SectionInstructionSet]:
        return self._instruction_set

    def contents_description(self) -> docs.SectionContents:
        return docs.section_contents([docs.para('Consists of zero or more instructions.')] +
                                     self.instruction_purpose_description())

    def instruction_purpose_description(self) -> List[ParagraphItem]:
        raise NotImplementedError()


class TestSuiteSectionDocumentationBaseForSectionWithoutInstructions(TestSuiteSectionDocumentation):
    def __init__(self, name: str):
        super().__init__(TestSuiteSectionWithoutInstructionsInfo(name))

    @property
    def has_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> SectionInstructionSet:
        return None
