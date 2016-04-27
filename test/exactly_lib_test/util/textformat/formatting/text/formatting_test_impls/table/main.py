import unittest

from exactly_lib.util.textformat.structure.table import Table, TableFormat, single_paragraph_cell, empty_cell
from exactly_lib_test.util.textformat.test_resources.constr import formatter_with_page_width, single_text_para


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


class TestEmpty(unittest.TestCase):
    def test_no_rows(self):
        # ARRANGE
        table = Table(TableFormat('|'),
                      [])
        formatter = formatter_with_page_width(5)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        self.assertEqual([],
                         actual)

    def test_single_row_single_empty_cell(self):
        # ARRANGE
        row = [empty_cell()]
        table = Table(TableFormat('|'),
                      [row])
        formatter = formatter_with_page_width(100)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        self.assertEqual([],
                         actual)

    def test_two_row_one_emtpy_cell(self):
        # ARRANGE
        row1 = [_text_cell('row 1/col 1'), empty_cell()]
        row2 = [_text_cell('row 2/col 1'), _text_cell('row 2/col 2')]
        table = Table(TableFormat('|'),
                      [row1,
                       row2])
        formatter = formatter_with_page_width(100)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        self.assertEqual(['row 1/col 1|           ',
                          'row 2/col 1|row 2/col 2'],
                         actual)


class TestUnderlineHeaderRow(unittest.TestCase):
    def test_WHEN_there_is_only_a_single_row_THEN_no_underline_should_be_rendered(self):
        # ARRANGE
        row1 = [_text_cell('row 1/cell 1')]
        table = Table(TableFormat('|', first_row_is_header=True),
                      [row1])
        formatter = formatter_with_page_width(100)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        self.assertEqual(['row 1/cell 1'],
                         actual)

    def test_multiple_rows_single_column(self):
        # ARRANGE
        row1 = [_text_cell('row 1/cell 1')]
        row2 = [_text_cell('row 2/cell 1')]
        table = Table(TableFormat('|', first_row_is_header=True),
                      [row1,
                       row2])
        formatter = formatter_with_page_width(100)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        self.assertEqual(['row 1/cell 1',
                          '------------',
                          'row 2/cell 1'],
                         actual)

    def test_multiple_rows_multiple_columns(self):
        # ARRANGE
        row1 = [_text_cell('row 1/cell 1'), _text_cell('1/2')]
        row2 = [_text_cell('row 2/cell 1'), _text_cell('2/2')]
        table = Table(TableFormat('|', first_row_is_header=True),
                      [row1,
                       row2])
        formatter = formatter_with_page_width(100)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        self.assertEqual(['row 1/cell 1|1/2',
                          '----------------',
                          'row 2/cell 1|2/2'],
                         actual)

    def test_multiple_rows_multiple_columns_with_multi_character_col_separator(self):
        # ARRANGE
        row1 = [_text_cell('row 1/cell 1'), _text_cell('1/2')]
        row2 = [_text_cell('row 2/cell 1'), _text_cell('2/2')]
        table = Table(TableFormat('<<>>', first_row_is_header=True),
                      [row1,
                       row2])
        formatter = formatter_with_page_width(100)
        # ACT #
        actual = formatter.format_table(table)
        # ASSERT #
        self.assertEqual(['row 1/cell 1<<>>1/2',
                          '-------------------',
                          'row 2/cell 1<<>>2/2'],
                         actual)


def _text_cell(text_as_string: str) -> list:
    return single_paragraph_cell(single_text_para(text_as_string))


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSingleRow),
        unittest.makeSuite(TestMultipleRows),
        unittest.makeSuite(TestEmpty),
        unittest.makeSuite(TestUnderlineHeaderRow),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
