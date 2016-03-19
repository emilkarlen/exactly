from shellcheck_lib.cli.execution_mode.help.mode.test_suite.contents_structure import TestSuiteHelp, \
    TestSuiteSectionHelp
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.paragraph import para


class TestSuiteHelpRenderer:
    def overview(self,
                 suite_help: TestSuiteHelp) -> doc.SectionContents:
        return doc.SectionContents([para('TODO: test suite overview help')], [])

    def section(self, section_help: TestSuiteSectionHelp) -> doc.SectionContents:
        return doc.SectionContents([para('TODO suite help for section ' + section_help.name)], [])
