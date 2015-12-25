import unittest

from shellcheck_lib.general.textformat import parse as sut
from shellcheck_lib_test.general.textformat.test_resources import parse as test_resource


class TestEmpty(unittest.TestCase):
    def test_empty_input(self):
        test_resource.check(self,
                            [],
                            sut.parse([]))


class TestSingleParagraphWithSingleText(unittest.TestCase):
    def test_single_text_block_on_single_line(self):
        test_resource.check(self,
                            [sut.Paragraph([sut.Text('the text block')])],
                            sut.parse(['the text block']))

    def test_single_text_block_on_multiple_lines(self):
        input_lines = ['the',
                       'text',
                       'block'
                       ]
        test_resource.check(self,
                            [sut.Paragraph([sut.Text(' '.join(input_lines))])],
                            sut.parse(input_lines))


class TestSingleParagraphWithMultipleTexts(unittest.TestCase):
    def test_single_line_text_blocks(self):
        test_resource.check(self,
                            [sut.Paragraph([sut.Text('text 1'),
                                            sut.Text('text 2')])],
                            sut.parse(['text 1'] +
                                      sut.TEXT_SEPARATOR_LINES +
                                      ['text 2']))

    def test_multi_line_text_blocks(self):
        input_lines = ['text',
                       '1'] + \
                      sut.TEXT_SEPARATOR_LINES + \
                      ['text',
                       '2']
        test_resource.check(self,
                            [sut.Paragraph([sut.Text('text 1'),
                                            sut.Text('text 2')])],
                            sut.parse(input_lines))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestEmpty))
    ret_val.addTest(unittest.makeSuite(TestSingleParagraphWithSingleText))
    ret_val.addTest(unittest.makeSuite(TestSingleParagraphWithMultipleTexts))
    return ret_val


if __name__ == '__main__':
    unittest.main()
