import unittest

from shellcheck_lib.util.textformat.structure.table import Table, TableFormat
from shellcheck_lib_test.util.textformat.test_resources.constr import formatter_with_page_width, single_text_para


class TestEmptyTable(unittest.TestCase):
    def test(self):
        # ARRANGE
        table = Table(TableFormat('|'),
                      [])
        formatter = formatter_with_page_width(5)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        self.assertEqual([],
                         actual)


class TestSingleRow(unittest.TestCase):
    def test_single_cell(self):
        # ARRANGE
        row1 = [[single_text_para('row 1/cell 1')]]
        table = Table(TableFormat('|'),
                      [row1])
        formatter = formatter_with_page_width(100)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        self.assertEqual(['row 1/cell 1'],
                         actual)

    def test_single_cell_with_word_wrap(self):
        # ARRANGE
        row1 = [[single_text_para('row 1 cell 1')]]
        table = Table(TableFormat('|'),
                      [row1])
        formatter = formatter_with_page_width(7)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        self.assertEqual(['row 1  ',
                          'cell 1 '],
                         actual)

    def test_multiple_cells(self):
        # ARRANGE
        row1 = [[single_text_para('row 1/cell 1')],
                [single_text_para('row 1/cell 2')]]
        table = Table(TableFormat('|'),
                      [row1])
        formatter = formatter_with_page_width(100)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        self.assertEqual(['row 1/cell 1|row 1/cell 2'],
                         actual)

    def test_multiple_cells_with_different_number_of_lines(self):
        # ARRANGE
        row1 = [[single_text_para('row 1/cell 1 para 1'),
                 single_text_para('row 1/cell 1 para 2')],
                [single_text_para('row 1/cell 2')]]
        table = Table(TableFormat('|'),
                      [row1])
        formatter = formatter_with_page_width(100)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        expected = ['row 1/cell 1 para 1|row 1/cell 2',
                    '                   |            ',
                    'row 1/cell 1 para 2|            ']
        self.assertEqual(expected,
                         actual)


class TestMultipleRows(unittest.TestCase):
    def test_multiple_rows_single_column(self):
        # ARRANGE
        row1 = [[single_text_para('row 1/cell 1')]]
        row2 = [[single_text_para('row 2/cell 1')]]
        table = Table(TableFormat('|'),
                      [row1,
                       row2])
        formatter = formatter_with_page_width(100)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        self.assertEqual(['row 1/cell 1',
                          'row 2/cell 1'],
                         actual)


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEmptyTable),
        unittest.makeSuite(TestSingleRow),
        unittest.makeSuite(TestMultipleRows),
    ])


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
