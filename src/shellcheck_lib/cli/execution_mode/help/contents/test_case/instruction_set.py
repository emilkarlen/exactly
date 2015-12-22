from shellcheck_lib.general.textformat.structure import document as doc
from shellcheck_lib.general.textformat.structure import lists
from shellcheck_lib.general.textformat.structure.core import Text
from shellcheck_lib.test_case.help.render.instruction import instruction_set_list_item
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup


def instruction_set(instruction_setup: InstructionsSetup) -> doc.SectionContents:
    sections = []
    for (phase, instruction_set_dict) in instruction_setup.phase_and_instruction_set:
        instruction_list = _instruction_list(instruction_set_dict)
        sections.append(doc.Section(Text(phase.identifier),
                                    doc.SectionContents([instruction_list], [])))
    return doc.SectionContents([], sections)


def _instruction_list(instruction_set_dict):
    instruction_list_items = []
    for (instruction_name, instruction_setup) in instruction_set_dict.items():
        description = instruction_setup.description
        list_item = instruction_set_list_item(description)
        instruction_list_items.append(list_item)
    return lists.HeaderValueList(lists.ListType.VARIABLE_LIST,
                                 instruction_list_items)
