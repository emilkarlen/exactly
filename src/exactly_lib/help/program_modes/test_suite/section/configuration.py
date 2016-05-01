from exactly_lib.help.program_modes.test_suite.section.common import \
    TestSuiteSectionDocumentationBaseForSectionWithoutInstructions
from exactly_lib.help.utils.description import Description
from exactly_lib.util.textformat.structure import structures as docs


class ConfigurationSectionDocumentation(TestSuiteSectionDocumentationBaseForSectionWithoutInstructions):
    def is_mandatory(self) -> bool:
        return False

    def contents_description(self) -> list:
        return [docs.para('TODO contents description of section {0}.'.format(self.name.syntax))]

    def purpose(self) -> Description:
        return Description(docs.text('TODO single line desc of section {0}'.format(self.name.syntax)),
                           [])
