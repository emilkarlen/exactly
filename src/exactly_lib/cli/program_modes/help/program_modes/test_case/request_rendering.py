import exactly_lib.help.program_modes.common.renderers
import exactly_lib.help.utils.render
from exactly_lib.cli.program_modes.help.program_modes.test_case.help_request import TestCaseHelpItem, \
    TestCaseHelpRequest
from exactly_lib.cli.program_modes.help.program_modes.utils import with_or_without_name
from exactly_lib.help.program_modes.common import render_instruction
from exactly_lib.help.program_modes.common.renderers import SectionDocumentationRenderer
from exactly_lib.help.program_modes.test_case.contents.cli_syntax import TestCaseCliSyntaxDocumentation
from exactly_lib.help.program_modes.test_case.contents.main.specification import SpecificationRenderer
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.program_modes.test_case.render import instruction_set
from exactly_lib.help.utils.cli_program_documentation_rendering import ProgramDocumentationSectionContentsRenderer
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import para, text


class TestCaseHelpRendererResolver:
    def __init__(self,
                 contents: TestCaseHelp):
        self._contents = contents

    def resolve(self, request: TestCaseHelpRequest) -> SectionContentsRenderer:
        item = request.item
        if item is TestCaseHelpItem.CLI_SYNTAX:
            return ProgramDocumentationSectionContentsRenderer(TestCaseCliSyntaxDocumentation())
        if item is TestCaseHelpItem.SPECIFICATION:
            return SpecificationRenderer(self._contents)
        if item is TestCaseHelpItem.INSTRUCTION_SET:
            return instruction_set.InstructionSetPerPhaseRenderer(self._contents)
        if item is TestCaseHelpItem.PHASE:
            return SectionDocumentationRenderer(request.data)
        if item is TestCaseHelpItem.PHASE_INSTRUCTION_LIST:
            return exactly_lib.help.program_modes.common.renderers.SectionInstructionSetRenderer(request.data)
        if item is TestCaseHelpItem.INSTRUCTION:
            return with_or_without_name(request.do_include_name_in_output,
                                        request.name,
                                        render_instruction.InstructionManPageRenderer(request.data))
        if item is TestCaseHelpItem.INSTRUCTION_SEARCH:
            return InstructionSearchRenderer(request.name,
                                             request.data)
        raise ValueError('Invalid %s: %s' % (str(TestCaseHelpItem), str(item)))


class InstructionSearchRenderer(SectionContentsRenderer):
    def __init__(self,
                 instruction_name: str,
                 phase_and_instruction_description_list: list):
        self.instruction_name = instruction_name
        self.phase_and_instruction_description_list = phase_and_instruction_description_list

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        sections = []
        for phase_and_instruction_description in self.phase_and_instruction_description_list:
            man_page_renderer = render_instruction.InstructionManPageRenderer(phase_and_instruction_description[1])
            phase_section = doc.Section(text(phase_and_instruction_description[0].syntax),
                                        man_page_renderer.apply(environment))
            sections.append(phase_section)
        initial_paragraphs = []
        if len(self.phase_and_instruction_description_list) > 1:
            initial_paragraphs = [para('The instruction "%s" exists in multiple phases.' % self.instruction_name)]
        return doc.SectionContents(initial_paragraphs, sections)
