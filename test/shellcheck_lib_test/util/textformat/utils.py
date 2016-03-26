import enum
import unittest

from shellcheck_lib.util.textformat.structure import core
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure import utils as sut
from shellcheck_lib.util.textformat.structure.literal_layout import LiteralLayout
from shellcheck_lib.util.textformat.structure.paragraph import Paragraph
from shellcheck_lib.util.textformat.structure.table import Table, TableFormat
from shellcheck_lib_test.util.textformat.test_resources.constr import single_text_para


class TestParagraphItemVisitor(unittest.TestCase):
    def test_visit_paragraph(self):
        # ARRANGE #
        item = single_text_para('paragraph text')
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        visitor.visit(item)
        # ASSERT #
        self.assertEqual([ItemType.PARAGRAPH],
                         visitor.visited_types)

    def test_visit_list(self):
        # ARRANGE #
        list_item = lists.HeaderContentListItem(core.Text('item text'), [])
        item = lists.HeaderContentList([list_item],
                                       lists.Format(lists.ListType.ITEMIZED_LIST))
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        visitor.visit(item)
        # ASSERT #
        self.assertEqual([ItemType.LIST],
                         visitor.visited_types)

    def test_visit_literal_layout(self):
        # ARRANGE #
        item = LiteralLayout('literal text')
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        visitor.visit(item)
        # ASSERT #
        self.assertEqual([ItemType.LITERAL_LAYOUT],
                         visitor.visited_types)

    def test_visit_table(self):
        # ARRANGE #
        item = Table(TableFormat('column separator'), [])
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        visitor.visit(item)
        # ASSERT #
        self.assertEqual([ItemType.TABLE],
                         visitor.visited_types)

    def test_visit_unknown_object(self):
        # ARRANGE #
        item = 'A value of a type that is not a ParagraphItem'
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        with self.assertRaises(ValueError):
            visitor.visit(item)
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')


class AVisitorThatRecordsVisitedMethods(sut.ParagraphItemVisitor):
    def __init__(self):
        self.visited_types = []

    def visit_paragraph(self, paragraph: Paragraph):
        self.visited_types.append(ItemType.PARAGRAPH)

    def visit_header_value_list(self, header_value_list: lists.HeaderContentList):
        self.visited_types.append(ItemType.LIST)

    def visit_literal_layout(self, x: LiteralLayout):
        self.visited_types.append(ItemType.LITERAL_LAYOUT)

    def visit_table(self, table: Table):
        self.visited_types.append(ItemType.TABLE)


class ItemType(enum.Enum):
    PARAGRAPH = 1
    LIST = 2
    LITERAL_LAYOUT = 3
    TABLE = 4


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParagraphItemVisitor)


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
