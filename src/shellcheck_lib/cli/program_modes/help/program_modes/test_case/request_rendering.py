from shellcheck_lib.cli.program_modes.help.program_modes.test_case.help_request import TestCaseHelpItem, \
    TestCaseHelpRequest
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCaseHelp, TestCasePhaseDocumentation
from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InstructionDocumentation
from shellcheck_lib.help.program_modes.test_case.render import instruction_set, render_instruction
from shellcheck_lib.help.program_modes.test_case.render.test_case_phase import render_test_case_phase_overview
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.core import Text
from shellcheck_lib.util.textformat.structure.structures import para


class TestCaseHelpRenderer:
    def __init__(self, contents: TestCaseHelp):
        self._contents = contents

    def render(self, request: TestCaseHelpRequest) -> doc.SectionContents:
        item = request.item
        if item is TestCaseHelpItem.OVERVIEW:
            return self.overview(self._contents)
        if item is TestCaseHelpItem.INSTRUCTION_SET:
            return self.instruction_set(self._contents)
        if item is TestCaseHelpItem.PHASE:
            return self.phase(request.data)
        if item is TestCaseHelpItem.PHASE_INSTRUCTION_LIST:
            return self.phase_instruction_list(request.data)
        if item is TestCaseHelpItem.INSTRUCTION:
            return self.instruction(request.data)
        if item is TestCaseHelpItem.INSTRUCTION_SEARCH:
            return self.instruction_search(request.name, request.data)
        raise ValueError('Invalid %s: %s' % (str(TestCaseHelpItem), str(item)))

    def overview(self, test_case_help: TestCaseHelp) -> doc.SectionContents:
        from shellcheck_lib.help.program_modes.test_case.contents.main.overview import overview_documentation
        return overview_documentation(test_case_help)

    def phase(self, phase_help: TestCasePhaseDocumentation) -> doc.SectionContents:
        return render_test_case_phase_overview(phase_help)

    def phase_instruction_list(self, phase_help: TestCasePhaseDocumentation) -> doc.SectionContents:
        return instruction_set.phase_instruction_set(phase_help.instruction_set)

    def instruction_set(self, test_case_help: TestCaseHelp) -> doc.SectionContents:
        return instruction_set.instruction_set_per_phase(test_case_help)

    def instruction(self, description: InstructionDocumentation) -> doc.SectionContents:
        return render_instruction.instruction_man_page(description)

    def instruction_search(self,
                           instruction_name: str,
                           phase_and_instruction_description_list: list) -> doc.SectionContents:
        sections = []
        for phase_and_instruction_description in phase_and_instruction_description_list:
            man_page = self.instruction(phase_and_instruction_description[1])
            phase_section = doc.Section(Text(phase_and_instruction_description[0].syntax),
                                        man_page)
            sections.append(phase_section)
        initial_paragraphs = []
        if len(phase_and_instruction_description_list) > 1:
            initial_paragraphs = [para('The instruction "%s" exists in multiple phases.' % instruction_name)]
        return doc.SectionContents(initial_paragraphs, sections)
