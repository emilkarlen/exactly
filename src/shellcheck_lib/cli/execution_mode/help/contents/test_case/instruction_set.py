from shellcheck_lib.general.textformat.structure import document as doc
from shellcheck_lib.general.textformat.structure import lists
from shellcheck_lib.general.textformat.structure.core import Text
from shellcheck_lib.general.textformat.structure.paragraph import para
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
        description_para = para(instruction_setup.description.single_line_description())
        instruction_list_items.append(lists.HeaderValueListItem(Text(instruction_name),
                                                                [description_para]))
    return lists.HeaderValueList(lists.ListType.VARIABLE_LIST,
                                 instruction_list_items)
