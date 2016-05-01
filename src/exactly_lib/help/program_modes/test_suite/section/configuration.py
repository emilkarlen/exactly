from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_suite.section.common import \
    TestSuiteSectionDocumentationForSectionWithInstructions
from exactly_lib.help.utils.description import Description
from exactly_lib.util.textformat.structure import structures as docs


class ConfigurationSectionDocumentation(TestSuiteSectionDocumentationForSectionWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)

    def instruction_purpose_description(self) -> list:
        return [docs.para('TODO conf section instruction purpose')]

    def is_mandatory(self) -> bool:
        return False

    def contents_description(self) -> list:
        return [docs.para('TODO contents description of section {0}.'.format(self.name.syntax))]

    def purpose(self) -> Description:
        return Description(docs.text('TODO single line desc of section {0}'.format(self.name.syntax)),
                           [])
