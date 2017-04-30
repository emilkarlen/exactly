import unittest
from html.entities import codepoint2name

from exactly_lib.util.textformat.formatting.html import entity_conversion as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_empty_input(self):
        s = ''
        actual = sut.convert(s)
        self.assertEquals(s, actual)

    def test_WHEN_no_entity_characters_are_in_the_string_THEN_the_input_should_be_returned(self):
        s = 'abc123'
        actual = sut.convert(s)
        self.assertEquals(s, actual)

    def test_string_with_entity_characters(self):
        cases = [
            (
                '§',
                '&{};'.format(codepoint2name[ord('§')])
            ),
            (
                '<>',
                '&{};&{};'.format(codepoint2name[ord('<')],
                                  codepoint2name[ord('>')])
            ),
            (
                'a§b"c',
                'a&{};b&{};c'.format(codepoint2name[ord('§')],
                                     codepoint2name[ord('"')])
            ),
        ]
        for input_string, expected_output in cases:
            with self.subTest(msg=input_string):
                actual = sut.convert(input_string)
                self.assertEquals(expected_output, actual)
