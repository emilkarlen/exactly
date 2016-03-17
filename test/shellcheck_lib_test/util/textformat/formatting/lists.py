import unittest

from shellcheck_lib.util.textformat.formatting import lists as sut
from shellcheck_lib.util.textformat.structure import core
from shellcheck_lib.util.textformat.structure import paragraph


class TestHeaderAndIndentFormatWithMarker(unittest.TestCase):
    def test_header_text(self):
        formatter = sut.HeaderAndIndentFormatWithMarker(marker='MARKER',
                                                        contents_indent_spaces=3)
        actual = formatter.header_text(1, 1, text('header'))
        self.assertEqual(text('MARKER header').value,
                         actual.value)

    def test_value_indent(self):
        formatter = sut.HeaderAndIndentFormatWithMarker(marker='MARKER',
                                                        contents_indent_spaces=5)
        actual = formatter.contents_indent(1)
        self.assertEqual(5 * ' ',
                         actual)

    def test_following_header_lines_indent(self):
        formatter = sut.HeaderAndIndentFormatWithMarker(marker='MARKER',
                                                        contents_indent_spaces=5)
        actual = formatter.following_header_lines_indent(1, 10)
        self.assertEqual((len('MARKER') + 1) * ' ',
                         actual)


class TestHeaderAndIndentFormatPlain(unittest.TestCase):
    def test_header_text(self):
        formatter = sut.HeaderAndIndentFormatPlain(contents_indent_spaces=5)
        actual = formatter.header_text(1, 1, text('header'))
        self.assertEqual(text('header').value,
                         actual.value)

    def test_value_indent(self):
        formatter = sut.HeaderAndIndentFormatPlain(contents_indent_spaces=7)
        actual = formatter.contents_indent(1)
        self.assertEqual(7 * ' ',
                         actual)

    def test_following_header_lines_indent(self):
        formatter = sut.HeaderAndIndentFormatPlain(contents_indent_spaces=5)
        actual = formatter.following_header_lines_indent(1, 10)
        self.assertEqual('',
                         actual)


class TestHeaderAndIndentFormatWithNumbering(unittest.TestCase):
    def test_header_text__element_number_1(self):
        formatter = sut.HeaderAndIndentFormatWithNumbering(contents_indent_spaces=5)
        actual = formatter.header_text(1, 1, text('header'))
        self.assertEqual(text('1. header').value,
                         actual.value)

    def test_header_text__element_number_2(self):
        formatter = sut.HeaderAndIndentFormatWithNumbering(contents_indent_spaces=5)
        actual = formatter.header_text(2, 1, text('header'))
        self.assertEqual(text('2. header').value,
                         actual.value)

    def test_value_indent(self):
        formatter = sut.HeaderAndIndentFormatWithNumbering(contents_indent_spaces=7)
        actual = formatter.contents_indent(1)
        self.assertEqual(7 * ' ',
                         actual)

    def test_following_header_lines_indent(self):
        formatter = sut.HeaderAndIndentFormatWithNumbering(contents_indent_spaces=7)
        actual = formatter.following_header_lines_indent(1, 10)
        self.assertEqual(len('1. ') * ' ',
                         actual)


def text(string: str) -> core.Text:
    return core.Text(string)


def para(texts: iter) -> paragraph.Paragraph:
    return paragraph.Paragraph(texts)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestHeaderAndIndentFormatPlain))
    ret_val.addTest(unittest.makeSuite(TestHeaderAndIndentFormatWithMarker))
    ret_val.addTest(unittest.makeSuite(TestHeaderAndIndentFormatWithNumbering))
    return ret_val


if __name__ == '__main__':
    unittest.main()
