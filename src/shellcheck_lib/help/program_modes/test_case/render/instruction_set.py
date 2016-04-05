from shellcheck_lib.help.program_modes.test_case.contents.main.utils import TestCaseHelpRendererBase
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseInstructionSet
from shellcheck_lib.help.program_modes.test_case.render.render_instruction import instruction_set_list_item
from shellcheck_lib.help.program_modes.test_case.render.utils import TestCasePhaseInstructionSetRendererBase
from shellcheck_lib.help.utils.render import RenderingEnvironment
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.structures import text


class PhaseInstructionSetRenderer(TestCasePhaseInstructionSetRendererBase):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        instruction_list = instruction_set_list(self.instruction_set)
        return doc.SectionContents([instruction_list], [])


class InstructionSetPerPhaseRenderer(TestCaseHelpRendererBase):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        sections = []
        for test_case_phase_help in self.test_case_help.phase_helps_in_order_of_execution:
            if test_case_phase_help.is_phase_with_instructions:
                instruction_list = instruction_set_list(test_case_phase_help.instruction_set)
                sections.append(doc.Section(text(test_case_phase_help.name.syntax),
                                            doc.SectionContents([instruction_list], [])))
        return doc.SectionContents([], sections)


def instruction_set_list(instruction_set: TestCasePhaseInstructionSet) -> lists.HeaderContentList:
    instruction_list_items = []
    for description in instruction_set.instruction_descriptions:
        list_item = instruction_set_list_item(description)
        instruction_list_items.append(list_item)
    return lists.HeaderContentList(instruction_list_items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0))
