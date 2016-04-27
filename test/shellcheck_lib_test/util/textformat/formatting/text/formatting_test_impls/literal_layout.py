import unittest

from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from shellcheck_lib_test.util.textformat.test_resources.constr import formatter_with_page_width


class TestLiteralLayout(unittest.TestCase):
    def test_empty(self):
        # ARRANGE
        literal_layout = LiteralLayout('')
        formatter = formatter_with_page_width(5)
        # ACT #
        actual = formatter.format_literal_layout(literal_layout)
        # ASSERT #
        self.assertEqual([],
                         actual)

    def test_single_line_that_is_shorter_than_the_page_width(self):
        # ARRANGE
        literal_layout = LiteralLayout('123')
        formatter = formatter_with_page_width(5)
        # ACT #
        actual = formatter.format_literal_layout(literal_layout)
        # ASSERT #
        self.assertEqual(['123'],
                         actual)

    def test_single_line_that_is_longer_than_the_page_width(self):
        # ARRANGE
        literal_layout = LiteralLayout('12 4567')
        formatter = formatter_with_page_width(5)
        # ACT #
        actual = formatter.format_literal_layout(literal_layout)
        # ASSERT #
        self.assertEqual(['12 45',
                          '67'],
                         actual)

    def test_multiple_lines(self):
        # ARRANGE
        literal_layout = LiteralLayout('12 4567\nabcdef')
        formatter = formatter_with_page_width(5)
        # ACT #
        actual = formatter.format_literal_layout(literal_layout)
        # ASSERT #
        self.assertEqual(['12 45',
                          '67',
                          'abcde',
                          'f'],
                         actual)


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestLiteralLayout)


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
