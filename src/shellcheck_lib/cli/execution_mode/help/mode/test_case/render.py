from shellcheck_lib.cli.execution_mode.help.mode.main_program.contents import test_case_overview_help
from shellcheck_lib.cli.execution_mode.help.mode.test_case.contents_structure import TestCaseHelp, TestCasePhaseHelp
from shellcheck_lib.cli.execution_mode.help.mode.test_case.help_request import TestCaseHelpItem, TestCaseHelpRequest
from shellcheck_lib.cli.execution_mode.help.render.test_case import instruction_set
from shellcheck_lib.document.syntax import phase_name_in_phase_syntax
from shellcheck_lib.help.test_case import instruction
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.core import Text
from shellcheck_lib.util.textformat.structure.paragraph import para


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
        if item is TestCaseHelpItem.INSTRUCTION_LIST:
            return self.instruction_list(request.name, request.data)
        raise ValueError('Invalid %s: %s' % (str(TestCaseHelpItem), str(item)))

    def overview(self, test_case_help: TestCaseHelp) -> doc.SectionContents:
        return doc.SectionContents(test_case_overview_help, [])

    def phase(self, phase_help: TestCasePhaseHelp) -> doc.SectionContents:
        return doc.SectionContents([para('TODO test-case help for phase ' + phase_help.name)], [])

    def phase_instruction_list(self, phase_help: TestCasePhaseHelp) -> doc.SectionContents:
        return instruction_set.phase_instruction_set(phase_help.instruction_set)

    def instruction_set(self, test_case_help: TestCaseHelp) -> doc.SectionContents:
        return instruction_set.instruction_set_per_phase(test_case_help)

    def instruction(self, description: Description) -> doc.SectionContents:
        return instruction.instruction_man_page(description)

    def instruction_list(self,
                         instruction_name: str,
                         phase_and_instruction_description_list: list) -> doc.SectionContents:
        sections = []
        for phase_and_instruction_description in phase_and_instruction_description_list:
            man_page = self.instruction(phase_and_instruction_description[1])
            phase_section = doc.Section(Text(phase_name_in_phase_syntax(phase_and_instruction_description[0])),
                                        man_page)
            sections.append(phase_section)
        initial_paragraphs = []
        if len(phase_and_instruction_description_list) > 1:
            initial_paragraphs = [para('The instruction "%s" is found in multiple phases.' % instruction_name)]
        return doc.SectionContents(initial_paragraphs, sections)
