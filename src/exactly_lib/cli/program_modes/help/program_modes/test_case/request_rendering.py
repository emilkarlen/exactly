from exactly_lib.cli.program_modes.help.program_modes.test_case.help_request import TestCaseHelpItem, \
    TestCaseHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.utils import with_or_without_name
from exactly_lib.help.program_modes.common import render_instruction
from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.common.renderers import instruction_set_constructor
from exactly_lib.help.program_modes.test_case.contents.cli_syntax import TestCaseCliSyntaxDocumentation
from exactly_lib.help.program_modes.test_case.contents.specification import main as tc_specification
from exactly_lib.help.program_modes.test_case.contents_structure.phase_documentation import TestCasePhaseDocumentation
from exactly_lib.help.program_modes.test_case.contents_structure.test_case_help import TestCaseHelp
from exactly_lib.help.program_modes.test_case.render import instruction_set
from exactly_lib.help.program_modes.test_case.render.phase_documentation import TestCasePhaseDocumentationConstructor
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.util.textformat.constructor import sections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import para, text


class TestCaseHelpConstructorResolver:
    def __init__(self,
                 contents: TestCaseHelp):
        self._contents = contents

    def resolve(self, request: TestCaseHelpRequest) -> SectionContentsConstructor:
        item = request.item
        if item is TestCaseHelpItem.CLI_SYNTAX:
            return ProgramDocumentationSectionContentsConstructor(TestCaseCliSyntaxDocumentation())
        if item is TestCaseHelpItem.SPECIFICATION:
            return tc_specification.as_section_contents_constructor(self._contents)
        if item is TestCaseHelpItem.INSTRUCTION_SET:
            return instruction_set.InstructionSetPerPhaseRenderer(self._contents)
        if item is TestCaseHelpItem.PHASE:
            assert isinstance(request.data, TestCasePhaseDocumentation), 'Must be a TestCasePhaseDoc'
            return sections.contents_from_article_contents(TestCasePhaseDocumentationConstructor(request.data))
        if item is TestCaseHelpItem.PHASE_INSTRUCTION_LIST:
            section_documentation = request.data
            assert isinstance(section_documentation, SectionDocumentation), 'Must be a SectionDocumentation'
            return instruction_set_constructor(section_documentation.instruction_set,
                                               instruction_group_by=section_documentation.instruction_group_by)
        if item is TestCaseHelpItem.INSTRUCTION:
            return with_or_without_name(request.do_include_name_in_output,
                                        request.name,
                                        render_instruction.InstructionDocArticleContentsConstructor(request.data))
        if item is TestCaseHelpItem.INSTRUCTION_SEARCH:
            return InstructionSearchConstructor(request.name,
                                                request.data)
        raise ValueError('Invalid %s: %s' % (str(TestCaseHelpItem), str(item)))


class InstructionSearchConstructor(SectionContentsConstructor):
    def __init__(self,
                 instruction_name: str,
                 phase_and_instruction_description_list: list):
        self.instruction_name = instruction_name
        self.phase_and_instruction_description_list = phase_and_instruction_description_list

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        sections = []
        for phase_and_instruction_description in self.phase_and_instruction_description_list:
            man_page_renderer = render_instruction.instruction_doc_section_contents_constructor(
                phase_and_instruction_description[1])
            phase_section = doc.Section(text(phase_and_instruction_description[0].syntax),
                                        man_page_renderer.apply(environment))
            sections.append(phase_section)
        initial_paragraphs = []
        if len(self.phase_and_instruction_description_list) > 1:
            initial_paragraphs = [para('The instruction "%s" exists in multiple phases.' % self.instruction_name)]
        return doc.SectionContents(initial_paragraphs, sections)
