from exactly_lib.cli.program_modes.help.program_modes.test_suite.help_request import TestSuiteHelpItem, \
    TestSuiteHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.utils import with_or_without_name
from exactly_lib.help.program_modes.common import render_instruction
from exactly_lib.help.program_modes.test_suite.contents import specification
from exactly_lib.help.program_modes.test_suite.contents.cli_syntax import SuiteCliSyntaxDocumentation
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.program_modes.test_suite.section.common import TestSuiteSectionDocumentation
from exactly_lib.help.program_modes.test_suite.section.render import TestSuiteSectionDocumentationRenderer
from exactly_lib.help.utils.cli_program.cli_program_documentation_rendering import \
    ProgramDocumentationSectionContentsRenderer
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.util.textformat.structure import document as doc


class TestSuiteHelpRendererResolver:
    def __init__(self, contents: TestSuiteHelp):
        self._contents = contents

    def resolve(self, request: TestSuiteHelpRequest) -> SectionContentsRenderer:
        item = request.item
        if item is TestSuiteHelpItem.CLI_SYNTAX:
            return ProgramDocumentationSectionContentsRenderer(SuiteCliSyntaxDocumentation())
        if item is TestSuiteHelpItem.SPECIFICATION:
            return specification.specification_renderer(self._contents)
        if item is TestSuiteHelpItem.SECTION:
            assert isinstance(request.data, TestSuiteSectionDocumentation), 'Must be a TestSuiteSectionDoc'
            return TestSuiteSectionDocumentationRenderer(request.data)

        if item is TestSuiteHelpItem.INSTRUCTION:
            return with_or_without_name(request.do_include_name_in_output,
                                        request.name,
                                        render_instruction.InstructionDocArticleContentsRenderer(request.data))
        raise ValueError('Invalid %s: %s' % (str(TestSuiteHelpItem), str(item)))

    def render(self, request: TestSuiteHelpRequest,
               environment: RenderingEnvironment) -> doc.SectionContents:
        return self.resolve(request).apply(environment)
