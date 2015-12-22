from shellcheck_lib.general.textformat.structure import document as doc, lists
from shellcheck_lib.general.textformat.structure.core import Text
from shellcheck_lib.general.textformat.structure.paragraph import para
from shellcheck_lib.test_case.help.instruction_description import Description


def instruction_man_page(description: Description) -> doc.SectionContents:
    return doc.SectionContents([para('TODO test-case help for instruction ' +
                                     description.instruction_name())],
                               [])


def instruction_set_list_item(description: Description) -> lists.HeaderValueListItem:
    description_para = para(description.single_line_description())
    return lists.HeaderValueListItem(Text(description.instruction_name()),
                                     [description_para])
