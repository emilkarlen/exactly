from typing import List

from exactly_lib.help.program_modes.test_suite.cont_struct.section_documentation import \
    TestSuiteSectionDocumentationBaseForSectionWithoutInstructions
from exactly_lib.help.program_modes.test_suite.contents.section.common import file_ref_contents_description
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem


class CasesSectionDocumentation(TestSuiteSectionDocumentationBaseForSectionWithoutInstructions):
    def contents_description(self) -> List[ParagraphItem]:
        return file_ref_contents_description('case')

    def purpose(self) -> Description:
        return Description(docs.text('Lists the test cases that are part of the suite.'),
                           [])
