from exactly_lib.help.program_modes.test_suite.contents.section.common import path_contents_description
from exactly_lib.help.program_modes.test_suite.contents_structure.section_documentation import \
    TestSuiteSectionDocumentationBaseForSectionWithoutInstructions
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure import structures as docs


class CasesSectionDocumentation(TestSuiteSectionDocumentationBaseForSectionWithoutInstructions):
    def contents_description(self) -> docs.SectionContents:
        return docs.section_contents(path_contents_description('case'))

    def purpose(self) -> Description:
        return Description(docs.text('Lists the test cases that are part of the suite.'),
                           [])
