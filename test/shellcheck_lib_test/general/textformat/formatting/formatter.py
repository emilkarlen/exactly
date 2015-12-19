import unittest

from shellcheck_lib.general.textformat.formatting import formatter as sut
from shellcheck_lib.general.textformat.structure import core
from shellcheck_lib.general.textformat.structure import paragraph


class TestParagraph(unittest.TestCase):
    def test_single_new_line_block(self):
        p = para([text('1234 12 34')])
        formatter = sut.Formatter(page_width=5)
        actual = formatter.format_paragraph(p)
        self.assertEqual(['1234',
                          '12 34'],
                         actual)

    def test_single_new_line_block_with_alternate_page_width(self):
        p = para([text('1234 67 90')])
        formatter = sut.Formatter(page_width=7)
        actual = formatter.format_paragraph(p)
        self.assertEqual(['1234 67',
                          '90'],
                         actual)

    def test_multiple_new_line_blocks(self):
        p = para([text('1234 12'),
                  text('34 5678')])
        formatter = sut.Formatter(page_width=5)
        actual = formatter.format_paragraph(p)
        self.assertEqual(['1234',
                          '12',
                          '34',
                          '5678'],
                         actual)


class TestParagraphItems(unittest.TestCase):
    def test_no_item(self):
        formatter = sut.Formatter(page_width=5,
                                  num_item_separator_lines=1)
        actual = formatter.format_paragraph_items([])
        self.assertEqual([],
                         actual)

    def test_single_item(self):
        p = para([text('1234 12 34')])
        formatter = sut.Formatter(page_width=5,
                                  num_item_separator_lines=1)
        actual = formatter.format_paragraph_items([p])
        self.assertEqual(['1234',
                          '12 34'],
                         actual)

    def test_multiple_items_with_zero_separator_lines(self):
        p1 = para([text('1234 12 34')])
        p2 = para([text('abc')])
        formatter = sut.Formatter(page_width=5,
                                  num_item_separator_lines=0)
        actual = formatter.format_paragraph_items([p1, p2])
        self.assertEqual(['1234',
                          '12 34',
                          'abc'],
                         actual)

    def test_multiple_items_with_non_zero_separator_lines(self):
        p1 = para([text('1234 12 34')])
        p2 = para([text('abc')])
        formatter = sut.Formatter(page_width=5,
                                  num_item_separator_lines=2)
        actual = formatter.format_paragraph_items([p1, p2])
        self.assertEqual(['1234',
                          '12 34',
                          '',
                          '',
                          'abc'],
                         actual)


def text(string='1234 12 34') -> core.Text:
    return core.Text(string)


def para(texts: iter) -> paragraph.Paragraph:
    return paragraph.Paragraph(texts)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParagraph))
    ret_val.addTest(unittest.makeSuite(TestParagraphItems))
    return ret_val


if __name__ == '__main__':
    unittest.main()
