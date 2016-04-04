from shellcheck_lib.cli.program_modes.help.program_modes.test_case.help_request import TestCaseHelpItem, \
    TestCaseHelpRequest
from shellcheck_lib.help.program_modes.test_case.contents.main.overview import OverviewRenderer
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from shellcheck_lib.help.program_modes.test_case.render import instruction_set, render_instruction
from shellcheck_lib.help.program_modes.test_case.render.test_case_phase import TestCasePhaseOverviewRenderer
from shellcheck_lib.help.utils.render import SectionContentsRenderer
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.structures import para, text


class TestCaseHelpRendererResolver:
    def __init__(self, contents: TestCaseHelp):
        self._contents = contents

    def resolve(self, request: TestCaseHelpRequest) -> SectionContentsRenderer:
        item = request.item
        if item is TestCaseHelpItem.OVERVIEW:
            return OverviewRenderer(self._contents)
        if item is TestCaseHelpItem.INSTRUCTION_SET:
            return instruction_set.InstructionSetPerPhaseRenderer(self._contents)
        if item is TestCaseHelpItem.PHASE:
            return TestCasePhaseOverviewRenderer(request.data)
        if item is TestCaseHelpItem.PHASE_INSTRUCTION_LIST:
            return instruction_set.PhaseInstructionSetRenderer(request.data)
        if item is TestCaseHelpItem.INSTRUCTION:
            return render_instruction.InstructionManPageRenderer(request.data)
        if item is TestCaseHelpItem.INSTRUCTION_SEARCH:
            return InstructionSearchRenderer(request.name, request.data)
        raise ValueError('Invalid %s: %s' % (str(TestCaseHelpItem), str(item)))


class InstructionSearchRenderer(SectionContentsRenderer):
    def __init__(self,
                 instruction_name: str,
                 phase_and_instruction_description_list: list):
        self.instruction_name = instruction_name
        self.phase_and_instruction_description_list = phase_and_instruction_description_list

    def apply(self) -> doc.SectionContents:
        sections = []
        for phase_and_instruction_description in self.phase_and_instruction_description_list:
            man_page_renderer = render_instruction.InstructionManPageRenderer(phase_and_instruction_description[1])
            phase_section = doc.Section(text(phase_and_instruction_description[0].syntax),
                                        man_page_renderer.apply())
            sections.append(phase_section)
        initial_paragraphs = []
        if len(self.phase_and_instruction_description_list) > 1:
            initial_paragraphs = [para('The instruction "%s" exists in multiple phases.' % self.instruction_name)]
        return doc.SectionContents(initial_paragraphs, sections)
