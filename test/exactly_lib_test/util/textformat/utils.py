import unittest

from exactly_lib.util.textformat.structure import core
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import utils as sut
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib.util.textformat.structure.table import Table, TableFormat


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParagraphItemVisitor)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestParagraphItemVisitor(unittest.TestCase):
    def test_visit_paragraph(self):
        # ARRANGE #
        item = Paragraph([StringText('string text')])
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(item)
        # ASSERT #
        self.assertEqual([Paragraph],
                         visitor.visited_types)
        self.assertIs(item,
                      ret_val)

    def test_visit_list(self):
        # ARRANGE #
        list_item = lists.HeaderContentListItem(core.StringText('item text'), [])
        item = lists.HeaderContentList([list_item],
                                       lists.Format(lists.ListType.ITEMIZED_LIST))
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(item)
        # ASSERT #
        self.assertEqual([lists.HeaderContentList],
                         visitor.visited_types)
        self.assertIs(item,
                      ret_val)

    def test_visit_literal_layout(self):
        # ARRANGE #
        item = LiteralLayout('literal text')
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(item)
        # ASSERT #
        self.assertEqual([LiteralLayout],
                         visitor.visited_types)
        self.assertIs(item,
                      ret_val)

    def test_visit_table(self):
        # ARRANGE #
        item = Table(TableFormat('column separator'), [])
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        ret_val = visitor.visit(item)
        # ASSERT #
        self.assertEqual([Table],
                         visitor.visited_types)
        self.assertIs(item,
                      ret_val)

    def test_visit_unknown_object(self):
        # ARRANGE #
        item = 'A value of a type that is not a ParagraphItem'
        visitor = AVisitorThatRecordsVisitedMethods()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(item)
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')


class AVisitorThatRecordsVisitedMethods(sut.ParagraphItemVisitor):
    def __init__(self):
        self.visited_types = []

    def visit_paragraph(self, paragraph: Paragraph):
        self.visited_types.append(Paragraph)
        return paragraph

    def visit_header_value_list(self, header_value_list: lists.HeaderContentList):
        self.visited_types.append(lists.HeaderContentList)
        return header_value_list

    def visit_literal_layout(self, x: LiteralLayout):
        self.visited_types.append(LiteralLayout)
        return x

    def visit_table(self, table: Table):
        self.visited_types.append(Table)
        return table
