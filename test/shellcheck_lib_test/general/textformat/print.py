import unittest

from shellcheck_lib.general.textformat import print as sut
from shellcheck_lib.general.textformat import structure


class TestParagraph(unittest.TestCase):
    def test_single_new_line_block(self):
        para = structure.Paragraph(['1234 12 34'])
        printer = sut.Formatter(page_width=5)
        actual = printer.format_paragraph(para)
        self.assertEqual(['1234',
                          '12 34'],
                         actual)

    def test_multiple_new_line_blocks(self):
        para = structure.Paragraph(['1234 12',
                                    '34 5678'])
        printer = sut.Formatter(page_width=5)
        actual = printer.format_paragraph(para)
        self.assertEqual(['1234',
                          '12',
                          '34',
                          '5678'],
                         actual)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParagraph))
    return ret_val


if __name__ == '__main__':
    unittest.main()
