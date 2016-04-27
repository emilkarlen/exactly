import unittest

from exactly_lib.util.textformat.formatting.text.table import width_distribution as sut


class TestSingleColumn(unittest.TestCase):
    def test_WHEN_column_fits_within_available_width_THEN_column_width_should_be_equal_to_column(self):
        column_content_width = 10
        column_content_widths = [column_content_width]
        available_width = column_content_width + 1
        distribution = sut.distribute_width(column_content_widths, available_width)
        self.assertEqual([column_content_width],
                         distribution)

    def test_WHEN_column_does_not_fit_within_available_width_THEN_column_width_should_be_equal_to_available_width(self):
        available_width = 10
        column_content_width = available_width + 1
        column_content_widths = [column_content_width]
        distribution = sut.distribute_width(column_content_widths, available_width)
        self.assertEqual([available_width],
                         distribution)

    def test_WHEN_column_contents_width_is_zero_THEN_column_width_should_be_zero(self):
        available_width = 10
        column_content_widths = [0]
        distribution = sut.distribute_width(column_content_widths, available_width)
        self.assertEqual([0],
                         distribution)


class TestTwoColumns(unittest.TestCase):
    def test_WHEN_one_column_contents_width_is_zero_THEN_that_column_width_should_be_zero(self):
        available_width = 10
        column_content_widths = [0, 15]
        distribution = sut.distribute_width(column_content_widths, available_width)
        self.assertEqual([0, 10],
                         distribution)

    def test_WHEN_available_width_cannot_be_equally_divided_THEN_starting_columns_should_get_one_unit_wider(self):
        column_content_widths = [100, 100, 100, 100]
        available_width = 42
        distribution = sut.distribute_width(column_content_widths, available_width)
        self.assertEqual([11, 11, 10, 10],
                         distribution)

    def test_WHEN_both_columns_fits_within_available_width_THEN_column_width_should_be_equal_to_column_width(self):
        column_content_widths = [10, 20]
        available_width = 100
        distribution = sut.distribute_width(column_content_widths, available_width)
        self.assertEqual([10, 20],
                         distribution)

    def test_WHEN_when_only_one_column_fits_THEN_the_other_column_should_get_all_remaining_width(self):
        column_content_widths = [10, 200]
        available_width = 50
        distribution = sut.distribute_width(column_content_widths, available_width)
        self.assertEqual([10, available_width - 10],
                         distribution)

    def test_WHEN_when_no_no_column_fits_THEN_all_columns_should_get_equal_width(self):
        column_content_widths = [100, 200]
        available_width = 50
        distribution = sut.distribute_width(column_content_widths, available_width)
        self.assertEqual([available_width / 2,
                          available_width / 2],
                         distribution)


class TestThreeColumns(unittest.TestCase):
    def test_distribute_remaining_space_on_first_unsatisfied_column(self):
        column_content_widths = [1, 12, 100]
        available_width = 30
        distribution = sut.distribute_width(column_content_widths, available_width)
        self.assertEqual([1,
                          12,
                          available_width - 12 - 1],
                         distribution)

    def test_distribute_remaining_space_on_second_unsatisfied_column(self):
        column_content_widths = [1, 100, 12]
        available_width = 30
        distribution = sut.distribute_width(column_content_widths, available_width)
        self.assertEqual([1,
                          available_width - 12 - 1,
                          12],
                         distribution)


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSingleColumn),
        unittest.makeSuite(TestTwoColumns),
        unittest.makeSuite(TestThreeColumns),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
