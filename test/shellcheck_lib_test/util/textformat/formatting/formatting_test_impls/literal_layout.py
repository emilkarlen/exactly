import unittest

from shellcheck_lib.util.textformat.formatting import paragraph_item as sut
from shellcheck_lib.util.textformat.structure.literal_layout import LiteralLayout


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


def formatter_with_page_width(page_width: int) -> sut.Formatter:
    return sut.Formatter(sut.Wrapper(page_width=page_width))


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestLiteralLayout)


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
