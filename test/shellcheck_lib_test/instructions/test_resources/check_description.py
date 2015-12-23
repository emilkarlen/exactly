import unittest

from shellcheck_lib.general.textformat.formatting import paragraph_item
from shellcheck_lib.general.textformat.formatting import section
from shellcheck_lib.general.textformat.formatting.wrapper import Wrapper
from shellcheck_lib.general.textformat.structure import lists
from shellcheck_lib.test_case.help.instruction_description import Description
from shellcheck_lib.test_case.help.render import instruction


class TestDescriptionBase(unittest.TestCase):
    """
    Tests a Description by rendering it with a Formatter
    (under the assumption that the Formatter is working).
    """

    def _description(self) -> Description:
        raise NotImplementedError()

    def setUp(self):
        self.formatter = section.Formatter(paragraph_item.Formatter(Wrapper(page_width=100)))
        self.description = self._description()

    def test_instruction_man_page(self):
        section_contents = instruction.instruction_man_page(self.description)
        self.formatter.format_section_contents(section_contents)

    def test_instruction_set_list_item(self):
        list_item = instruction.instruction_set_list_item(self.description)
        the_list = lists.HeaderValueList(lists.ListType.VARIABLE_LIST,
                                         [list_item])
        self.formatter.paragraph_item_formatter.format_header_value_list(the_list)
