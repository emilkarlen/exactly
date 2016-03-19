from shellcheck_lib.cli.execution_mode.help.mode.test_suite.contents_structure import TestSuiteHelp, \
    TestSuiteSectionHelp
from shellcheck_lib.cli.execution_mode.help.mode.test_suite.help_request import TestSuiteHelpItem, TestSuiteHelpRequest
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.paragraph import para


class TestSuiteHelpRenderer:
    def __init__(self, contents: TestSuiteHelp):
        self._contents = contents

    def render(self, request: TestSuiteHelpRequest) -> doc.SectionContents:
        item = request.item
        if item is TestSuiteHelpItem.OVERVIEW:
            return self.overview(self._contents)
        if item is TestSuiteHelpItem.SECTION:
            assert isinstance(request.data, TestSuiteSectionHelp)
            return self.section(request.data)
        raise ValueError('Invalid %s: %s' % (str(TestSuiteHelpItem), str(item)))

    def overview(self,
                 suite_help: TestSuiteHelp) -> doc.SectionContents:
        return doc.SectionContents([para('TODO: test suite overview help')], [])

    def section(self, section_help: TestSuiteSectionHelp) -> doc.SectionContents:
        return doc.SectionContents([para('TODO suite help for section ' + section_help.name)], [])
