from exactly_lib.cli.program_modes.help.program_modes.test_suite.help_request import TestSuiteHelpItem, \
    TestSuiteHelpRequest
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.common.renderers import SectionDocumentationRenderer
from exactly_lib.help.program_modes.test_suite.contents.cli_syntax import SuiteCliSyntaxDocumentation
from exactly_lib.help.program_modes.test_suite.contents.specification import SpecificationRenderer
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.cli_syntax.render.cli_program_syntax import ProgramDocumentationSectionContentsRenderer
from exactly_lib.util.textformat.structure import document as doc


class TestSuiteHelpRendererResolver:
    def __init__(self, contents: TestSuiteHelp):
        self._contents = contents

    def resolve(self, request: TestSuiteHelpRequest) -> SectionContentsRenderer:
        item = request.item
        if item is TestSuiteHelpItem.CLI_SYNTAX:
            return ProgramDocumentationSectionContentsRenderer(SuiteCliSyntaxDocumentation())
        if item is TestSuiteHelpItem.OVERVIEW:
            return SpecificationRenderer(self._contents)
        if item is TestSuiteHelpItem.SECTION:
            assert isinstance(request.data, SectionDocumentation)
            return SectionDocumentationRenderer(request.data)
        raise ValueError('Invalid %s: %s' % (str(TestSuiteHelpItem), str(item)))

    def render(self, request: TestSuiteHelpRequest,
               environment: RenderingEnvironment) -> doc.SectionContents:
        return self.resolve(request).apply(environment)
