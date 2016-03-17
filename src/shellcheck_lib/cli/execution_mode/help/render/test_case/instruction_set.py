from shellcheck_lib.cli.execution_mode.help.contents import TestCaseHelp, \
    TestCasePhaseInstructionSet
from shellcheck_lib.help.test_case.instruction import instruction_set_list_item
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure.core import Text


def instruction_set_per_phase(test_case_help: TestCaseHelp) -> doc.SectionContents:
    sections = []
    for test_case_phase_help in test_case_help.phase_helps:
        if test_case_phase_help.is_phase_with_instructions:
            instruction_list = _instruction_list(test_case_phase_help.instruction_set)
            sections.append(doc.Section(Text(test_case_phase_help.name),
                                        doc.SectionContents([instruction_list], [])))
    return doc.SectionContents([], sections)


def _instruction_list(instruction_set: TestCasePhaseInstructionSet) -> lists.HeaderContentList:
    instruction_list_items = []
    for description in instruction_set.instruction_descriptions:
        list_item = instruction_set_list_item(description)
        instruction_list_items.append(list_item)
    return lists.HeaderContentList(instruction_list_items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0))
