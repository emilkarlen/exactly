from exactly_lib.definitions.test_suite import file_names
from exactly_lib.help.program_modes.test_suite.contents.section.common import path_contents_description
from exactly_lib.help.program_modes.test_suite.contents_structure.section_documentation import \
    TestSuiteSectionDocumentationBaseForSectionWithoutInstructions
from exactly_lib.section_document.model import SectionContents
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


class SuitesSectionDocumentation(TestSuiteSectionDocumentationBaseForSectionWithoutInstructions):
    def contents_description(self) -> SectionContents:
        tp = TextParser({
            'default_suite_file_name': file_names.DEFAULT_SUITE_FILE,
        })
        return docs.section_contents(
            path_contents_description('suite'),
            [
                docs.section('Default suite file',
                             tp.fnap(_DIR_AS_SUITE))
            ]
        )

    def purpose(self) -> Description:
        return Description(docs.text('Lists test suites (sub suites) that are part of the suite.'),
                           [])


_DIR_AS_SUITE = """\
A directory serves as a suite file,
if it contains the default suite file "{default_suite_file_name}"
(which must be a test suite).
"""
