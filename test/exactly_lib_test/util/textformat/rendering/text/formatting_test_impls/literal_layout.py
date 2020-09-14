import unittest
from typing import List

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib_test.util.textformat.test_resources.constr import formatter_with_page_width


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestLiteralLayout)


class TestLiteralLayout(unittest.TestCase):
    def test_empty(self):
        # ARRANGE
        for indent_case in MAX_1_CHAR_INDENTS:
            with self.subTest(indent_case.name):
                formatter = formatter_with_page_width(5, literal_layout_indent=indent_case.value)
                literal_layout = LiteralLayout('')
                # ACT #
                actual = formatter.format_literal_layout(literal_layout)
                # ASSERT #
                self.assertEqual([],
                                 actual)

    def test_single_line_that_is_shorter_than_the_page_width(self):
        # ARRANGE
        for indent_case in MAX_1_CHAR_INDENTS:
            with self.subTest(indent_case.name):
                formatter = formatter_with_page_width(5, literal_layout_indent=indent_case.value)
                literal_layout = LiteralLayout('123')
                # ACT #
                actual = formatter.format_literal_layout(literal_layout)
                # ASSERT #
                self.assertEqual(
                    _lines_starting_with(indent_case.value,
                                         ['123']),
                    actual)

    def test_multiple_lines_that_is_shorter_than_the_page_width(self):
        # ARRANGE
        for indent_case in MAX_1_CHAR_INDENTS:
            with self.subTest(indent_case.name):
                formatter = formatter_with_page_width(5, literal_layout_indent=indent_case.value)
                literal_layout = LiteralLayout('123\n456')
                # ACT #
                actual = formatter.format_literal_layout(literal_layout)
                # ASSERT #
                self.assertEqual(
                    _lines_starting_with(indent_case.value,
                                         ['123', '456']),
                    actual)

    def test_single_line_that_is_longer_than_the_page_width__wo_indent(self):
        # ARRANGE
        literal_layout = LiteralLayout('12 4567')
        formatter = formatter_with_page_width(5)
        # ACT #
        actual = formatter.format_literal_layout(literal_layout)
        # ASSERT #
        self.assertEqual(['12 45',
                          '67'],
                         actual)

    def test_single_line_that_is_longer_than_the_page_width__w_indent(self):
        # ARRANGE
        literal_layout = LiteralLayout('12 4567')
        formatter = formatter_with_page_width(6, literal_layout_indent='x')
        # ACT #
        actual = formatter.format_literal_layout(literal_layout)
        # ASSERT #
        self.assertEqual(['x12 45',
                          'x67'],
                         actual)

    def test_multiple_lines(self):
        # ARRANGE
        formatter = formatter_with_page_width(5)
        literal_layout = LiteralLayout('12 4567\nabcdef')
        # ACT #
        actual = formatter.format_literal_layout(literal_layout)
        # ASSERT #
        self.assertEqual(['12 45',
                          '67',
                          'abcde',
                          'f'],
                         actual)


def _lines_starting_with(start: str, lines: List[str]) -> List[str]:
    return [
        start + line
        for line in lines
    ]


MAX_1_CHAR_INDENTS = [
    NameAndValue(
        'empty',
        ''
    ),
    NameAndValue(
        'single char',
        ' '
    ),
]
if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
