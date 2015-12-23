from shellcheck_lib.cli.execution_mode.help.contents import TestCaseHelp, \
    TestCasePhaseInstructionSet
from shellcheck_lib.general.textformat.structure import document as doc
from shellcheck_lib.general.textformat.structure import lists
from shellcheck_lib.general.textformat.structure.core import Text
from shellcheck_lib.test_case.help.render.instruction import instruction_set_list_item


def instruction_set(test_case_help: TestCaseHelp) -> doc.SectionContents:
    sections = []
    for test_case_phase_help in test_case_help.phase_helps:
        if test_case_phase_help.is_phase_with_instructions:
            instruction_list = _instruction_list(test_case_phase_help.instruction_set)
            sections.append(doc.Section(Text(test_case_phase_help.name),
                                        doc.SectionContents([instruction_list], [])))
    return doc.SectionContents([], sections)


def _instruction_list(instruction_set: TestCasePhaseInstructionSet):
    instruction_list_items = []
    for description in instruction_set.instruction_descriptions:
        list_item = instruction_set_list_item(description)
        instruction_list_items.append(list_item)
    return lists.HeaderValueList(lists.ListType.VARIABLE_LIST,
                                 instruction_list_items)
