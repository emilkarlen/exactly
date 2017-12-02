import unittest

from exactly_lib.util.textformat.rendering.text import paragraph_item as sut
from exactly_lib_test.util.textformat.test_resources.constr import text, para, BLANK_LINE, \
    CROSS_REF_TITLE_ONLY_TEXT_FORMATTER


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParagraphItems)


class TestParagraphItems(unittest.TestCase):
    def test_no_item(self):
        formatter = sut.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                  sut.Wrapper(5),
                                  num_item_separator_lines=1)
        actual = formatter.format_paragraph_items([])
        self.assertEqual([],
                         actual)

    def test_single_item(self):
        p = para([text('1234 12 34')])
        formatter = sut.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                  sut.Wrapper(5),
                                  num_item_separator_lines=1)
        actual = formatter.format_paragraph_items([p])
        self.assertEqual(['1234',
                          '12 34'],
                         actual)

    def test_multiple_items_with_zero_separator_lines(self):
        p1 = para([text('1234 12 34')])
        p2 = para([text('abc')])
        formatter = sut.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                  sut.Wrapper(5),
                                  num_item_separator_lines=0)
        actual = formatter.format_paragraph_items([p1, p2])
        self.assertEqual(['1234',
                          '12 34',
                          'abc'],
                         actual)

    def test_multiple_items_with_non_zero_separator_lines(self):
        p1 = para([text('1234 12 34')])
        p2 = para([text('abc')])
        formatter = sut.Formatter(CROSS_REF_TITLE_ONLY_TEXT_FORMATTER,
                                  sut.Wrapper(page_width=5),
                                  num_item_separator_lines=2)
        actual = formatter.format_paragraph_items([p1, p2])
        self.assertEqual(['1234',
                          '12 34',
                          BLANK_LINE,
                          BLANK_LINE,
                          'abc'],
                         actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
