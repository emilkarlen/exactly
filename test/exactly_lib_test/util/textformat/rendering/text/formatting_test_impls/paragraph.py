import unittest

from exactly_lib_test.util.textformat.test_resources.constr import text, para, formatter_with_page_width


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParagraph)


class TestParagraph(unittest.TestCase):
    def test_too_long_line(self):
        p = para([text('1234567')])
        formatter = formatter_with_page_width(5)
        actual = formatter.format_paragraph(p)
        self.assertEqual(['12345',
                          '67'],
                         actual)

    def test_single_new_line_block(self):
        p = para([text('1234 12 34')])
        formatter = formatter_with_page_width(5)
        actual = formatter.format_paragraph(p)
        self.assertEqual(['1234',
                          '12 34'],
                         actual)

    def test_single_new_line_block_with_alternate_page_width(self):
        p = para([text('1234 67 90')])
        formatter = formatter_with_page_width(7)
        actual = formatter.format_paragraph(p)
        self.assertEqual(['1234 67',
                          '90'],
                         actual)

    def test_multiple_new_line_blocks(self):
        p = para([text('1234 12'),
                  text('34 5678')])
        formatter = formatter_with_page_width(5)
        actual = formatter.format_paragraph(p)
        self.assertEqual(['1234',
                          '12',
                          '34',
                          '5678'],
                         actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
