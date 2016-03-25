import types
import unittest

from shellcheck_lib.util.textformat.formatting.table import column_max_width as sut


class TestCase(unittest.TestCase):
    def test_single_column_single_cell_with_available_width_wider_than_widest_cell(self):
        # ARRANGE #
        column1 = [['1234']]
        # ACT #
        actual = sut.derive_column_max_widths(paragraph_items_formatter_where_each_pi_must_be_a_plain_str,
                                              100,
                                              [column1])
        # ASSERT #
        self.assertEqual([4],
                         actual)

    def test_single_column_single_cell_with_available_width_narrower_than_widest_cell(self):
        # ARRANGE #
        column1 = [['1234']]
        # ACT #
        actual = sut.derive_column_max_widths(paragraph_items_formatter_where_each_pi_must_be_a_plain_str,
                                              2,
                                              [column1])
        # ASSERT #
        self.assertEqual([4],
                         actual)

    def test_single_column_multiple_cells(self):
        # ARRANGE #
        column1 = [['12',
                    '',
                    '1234',
                    '12']]
        # ACT #
        actual = sut.derive_column_max_widths(paragraph_items_formatter_where_each_pi_must_be_a_plain_str,
                                              100,
                                              [column1])
        # ASSERT #
        self.assertEqual([4],
                         actual)

    def test_multiple_columns(self):
        # ARRANGE #
        column1 = [['12',
                    '1234']]
        column2 = [['12',
                    '',
                    '12345']]
        # ACT #
        actual = sut.derive_column_max_widths(paragraph_items_formatter_where_each_pi_must_be_a_plain_str,
                                              100,
                                              [column1,
                                               column2])
        # ASSERT #
        self.assertEqual([4, 5],
                         actual)


def paragraph_items_formatter_where_each_pi_must_be_a_plain_str(available_width: int) -> types.FunctionType:
    def ret_val(paragraph_items: list):
        return paragraph_items

    return ret_val


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestCase)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
