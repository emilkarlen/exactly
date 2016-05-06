from exactly_lib.help.program_modes.test_suite.section.common import \
    TestSuiteSectionDocumentationBaseForSectionWithoutInstructions
from exactly_lib.help.program_modes.test_suite.section.common_contents import file_ref_contents_description
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure import structures as docs


class CasesSectionDocumentation(TestSuiteSectionDocumentationBaseForSectionWithoutInstructions):
    def is_mandatory(self) -> bool:
        return False

    def contents_description(self) -> list:
        return file_ref_contents_description('case')

    def purpose(self) -> Description:
        return Description(docs.text('Lists the test cases that are part of the suite.'),
                           [])
