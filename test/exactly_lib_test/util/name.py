import unittest

from exactly_lib.util import name as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(NameWithGenderWithFormattingTest)


class Case:
    def __init__(self,
                 name: str,
                 format_string: str,
                 expected: str):
        self.name = name
        self.format_string = format_string
        self.expected = expected


SC = sut.NameWithGenderWithFormatting


class NameWithGenderWithFormattingTest(unittest.TestCase):
    def test_get_parts(self):
        value = sut.NameWithGenderWithFormatting(sut.NameWithGender('det-word',
                                                                    'sing',
                                                                    'plur'),
                                                 '[',
                                                 ']')

        self.assertEqual('det-word',
                         value.determinator_word,
                         'determinator word')

        self.assertEqual('sing',
                         value.singular,
                         'singular')

        self.assertEqual('plur',
                         value.plural,
                         'plural')

        self.assertEqual('[',
                         value.quoting_begin,
                         'quoting_begin')

        self.assertEqual(']',
                         value.quoting_end,
                         'quoting_end')

    def test_default_SHOULD_be_singular(self):
        name = sut.NameWithGenderWithFormatting(sut.NameWithGender('a', 'name', 'names'),
                                                quoting_begin='<<',
                                                quoting_end='>>')
        self._check_with_flags(name,
                               name.singular,
                               '')

    def test_explicit_singular_spec_SHOULD_be_singular(self):
        name = sut.NameWithGenderWithFormatting(sut.NameWithGender('a', 'name', 'names'),
                                                quoting_begin='<<',
                                                quoting_end='>>')
        self._check_with_flags(name,
                               name.singular,
                               SC.SINGULAR)

    def test_plural(self):
        name = sut.NameWithGenderWithFormatting(sut.NameWithGender('a', 'name', 'names'),
                                                quoting_begin='<<',
                                                quoting_end='>>')
        self._check_with_flags(name,
                               name.plural,
                               SC.PLURAL)

    def test_denominator_word(self):
        name = sut.NameWithGenderWithFormatting(sut.NameWithGender('a', 'name', 'names'),
                                                quoting_begin='<<',
                                                quoting_end='>>')
        self._check_with_flags(name,
                               name.determinator_word,
                               SC.DETERMINATOR_WORD)

    def test_singular_determined(self):
        name = sut.NameWithGenderWithFormatting(sut.NameWithGender('an', 'instruction name', 'instruction names'),
                                                quoting_begin='[',
                                                quoting_end=']')
        self._check_with_flags(name,
                               name.singular_determined,
                               SC.DETERMINED)

    def _check_with_flags(self,
                          name: sut.NameWithGenderWithFormatting,
                          expected_element: str,
                          element_picker_format: str,
                          ):
        cases = [
            Case(
                'flags: none',
                '',
                expected=expected_element
            ),
            Case(
                'flags: quoted',
                SC.FLAG_SEPARATOR + SC.QUOTED_FLAG,
                expected=name.quoting_begin + expected_element + name.quoting_end
            ),
            Case(
                'flags:init_cap',
                SC.FLAG_SEPARATOR + SC.INIT_CAP_FLAG,
                expected=expected_element.capitalize()
            ),
            Case(
                'flags:upper',
                SC.FLAG_SEPARATOR + SC.UPPER_CASE_FLAG,
                expected=expected_element.upper()
            ),
            Case(
                'flags:upper quoted',
                SC.FLAG_SEPARATOR +
                SC.UPPER_CASE_FLAG +
                SC.QUOTED_FLAG,
                expected=name.quoting_begin + expected_element.upper() + name.quoting_end
            ),
            Case(
                'flags:quoted upper',
                SC.FLAG_SEPARATOR +
                SC.QUOTED_FLAG +
                SC.UPPER_CASE_FLAG,
                expected=name.quoting_begin + expected_element.upper() + name.quoting_end
            ),
        ]

        for case in cases:
            if not element_picker_format and not case.format_string:
                format_tail = ''
            else:
                format_tail = ':' + element_picker_format + case.format_string
            with self.subTest(name=case.name,
                              format_string=case.format_string,
                              format_tail=format_tail):
                string_to_format = '{{x{format_string}}}'.format(format_string=format_tail)
                actual = string_to_format.format(x=name)

            self.assertEqual(case.expected, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())