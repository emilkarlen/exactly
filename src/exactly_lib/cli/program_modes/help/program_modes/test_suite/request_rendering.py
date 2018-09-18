from exactly_lib.cli.program_modes.help.program_modes.test_suite.help_request import TestSuiteHelpItem, \
    TestSuiteHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.utils import with_or_without_name
from exactly_lib.help.program_modes.common import render_instruction
from exactly_lib.help.program_modes.test_suite.contents.cli_syntax import TestSuiteCliSyntaxDocumentation
from exactly_lib.help.program_modes.test_suite.contents.specification import main
from exactly_lib.help.program_modes.test_suite.contents_structure.section_documentation import \
    TestSuiteSectionDocumentation
from exactly_lib.help.program_modes.test_suite.contents_structure.test_suite_help import TestSuiteHelp
from exactly_lib.help.program_modes.test_suite.render.section_documentation import \
    TestSuiteSectionDocumentationConstructor
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.util.textformat.constructor import sections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.structure import document as doc


class TestSuiteHelpConstructorResolver:
    def __init__(self, contents: TestSuiteHelp):
        self._contents = contents

    def resolve(self, request: TestSuiteHelpRequest) -> SectionContentsConstructor:
        item = request.item
        if item is TestSuiteHelpItem.CLI_SYNTAX:
            return ProgramDocumentationSectionContentsConstructor(TestSuiteCliSyntaxDocumentation())
        if item is TestSuiteHelpItem.SPECIFICATION:
            return main.specification_constructor(self._contents)
        if item is TestSuiteHelpItem.SECTION:
            assert isinstance(request.data, TestSuiteSectionDocumentation), 'Must be a TestSuiteSectionDoc'
            return sections.contents_from_article_contents(TestSuiteSectionDocumentationConstructor(request.data))

        if item is TestSuiteHelpItem.INSTRUCTION:
            return with_or_without_name(request.do_include_name_in_output,
                                        request.name,
                                        render_instruction.InstructionDocArticleContentsConstructor(request.data))
        raise ValueError('Invalid %s: %s' % (str(TestSuiteHelpItem), str(item)))

    def render(self, request: TestSuiteHelpRequest,
               environment: ConstructionEnvironment) -> doc.SectionContents:
        return self.resolve(request).apply(environment)
