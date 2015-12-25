import unittest

from shellcheck_lib.general.textformat import parse as sut
from shellcheck_lib_test.general.textformat.test_resources import parse as test_resource


class TestEmpty(unittest.TestCase):
    def test_empty_input(self):
        test_resource.check(self,
                            [],
                            sut.parse([]))


class TestSingleParagraph(unittest.TestCase):
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


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestEmpty))
    ret_val.addTest(unittest.makeSuite(TestSingleParagraph))
    return ret_val


if __name__ == '__main__':
    unittest.main()
