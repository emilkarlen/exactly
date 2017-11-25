from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, \
    SectionDocumentation
from exactly_lib.help_texts.formatting import SectionName
from exactly_lib.util.textformat.structure import structures as docs


class TestSuiteSectionDocumentation(SectionDocumentation):
    def __init__(self, name: str):
        super().__init__(name)
        self._section_name = SectionName(name)

    def contents_description(self) -> list:
        """
        :return: [`ParagraphItem`]
        """
        raise NotImplementedError()


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
    def instruction_set(self) -> SectionInstructionSet:
        return self._instruction_set

    def contents_description(self) -> list:
        return [docs.para('Consists of zero or more instructions.')] + self.instruction_purpose_description()

    def instruction_purpose_description(self) -> list:
        """
        :return: [ParagraphItem]
        """
        raise NotImplementedError()


class TestSuiteSectionDocumentationBaseForSectionWithoutInstructions(TestSuiteSectionDocumentation):
    def __init__(self,
                 name: str):
        super().__init__(name)

    @property
    def has_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> SectionInstructionSet:
        return None
