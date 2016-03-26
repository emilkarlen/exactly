from shellcheck_lib.document.syntax import section_header
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseInstructionSet, \
    TestCaseHelp
from shellcheck_lib.help.program_modes.test_case.render.render_instruction import instruction_set_list_item
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.core import Text


def phase_instruction_set(instruction_set: TestCasePhaseInstructionSet) -> doc.SectionContents:
    instruction_list = instruction_set_list(instruction_set)
    return doc.SectionContents([instruction_list], [])


def instruction_set_per_phase(test_case_help: TestCaseHelp) -> doc.SectionContents:
    sections = []
    for test_case_phase_help in test_case_help.phase_helps_in_order_of_execution:
        if test_case_phase_help.is_phase_with_instructions:
            instruction_list = instruction_set_list(test_case_phase_help.instruction_set)
            sections.append(doc.Section(Text(section_header(test_case_phase_help.name)),
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
