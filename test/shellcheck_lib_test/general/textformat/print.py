import unittest

from shellcheck_lib.general.textformat import print as sut
from shellcheck_lib.general.textformat import structure as s


class TestParagraph(unittest.TestCase):
    def test_single_new_line_block(self):
        para = s.Paragraph([s.Text('1234 12 34')])
        formatter = sut.Formatter(page_width=5)
        actual = formatter.format_paragraph(para)
        self.assertEqual(['1234',
                          '12 34'],
                         actual)

    def test_single_new_line_block_with_alternate_page_width(self):
        para = s.Paragraph([s.Text('1234 67 90')])
        formatter = sut.Formatter(page_width=7)
        actual = formatter.format_paragraph(para)
        self.assertEqual(['1234 67',
                          '90'],
                         actual)

    def test_multiple_new_line_blocks(self):
        para = s.Paragraph([s.Text('1234 12'),
                            s.Text('34 5678')])
        formatter = sut.Formatter(page_width=5)
        actual = formatter.format_paragraph(para)
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
        para = s.Paragraph([s.Text('1234 12 34')])
        formatter = sut.Formatter(page_width=5,
                                  num_item_separator_lines=1)
        actual = formatter.format_paragraph_items([para])
        self.assertEqual(['1234',
                          '12 34'],
                         actual)

    def test_multiple_items_with_zero_separator_lines(self):
        para1 = s.Paragraph([s.Text('1234 12 34')])
        para2 = s.Paragraph([s.Text('abc')])
        formatter = sut.Formatter(page_width=5,
                                  num_item_separator_lines=0)
        actual = formatter.format_paragraph_items([para1, para2])
        self.assertEqual(['1234',
                          '12 34',
                          'abc'],
                         actual)

    def test_multiple_items_with_non_zero_separator_lines(self):
        para1 = s.Paragraph([s.Text('1234 12 34')])
        para2 = s.Paragraph([s.Text('abc')])
        formatter = sut.Formatter(page_width=5,
                                  num_item_separator_lines=2)
        actual = formatter.format_paragraph_items([para1, para2])
        self.assertEqual(['1234',
                          '12 34',
                          '',
                          '',
                          'abc'],
                         actual)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParagraph))
    ret_val.addTest(unittest.makeSuite(TestParagraphItems))
    return ret_val


if __name__ == '__main__':
    unittest.main()
