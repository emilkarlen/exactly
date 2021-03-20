import unittest

from exactly_lib.util.str_ import name as sut
from exactly_lib_test.test_resources.test_utils import NEA


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(NumberOfItemsStringTest),
        unittest.makeSuite(NameWithGenderWithFormattingTest),
    ])


class NumberOfItemsStringTest(unittest.TestCase):
    def runTest(self):
        singular = 'singular'
        plural = 'plural'

        test_object = sut.NumberOfItemsString(sut.Name(singular,
                                                       plural))

        cases = [
            NEA('1',
                '1 ' + singular,
                1),
            NEA('2',
                '2 ' + plural,
                2),
            NEA('0',
                '0 ' + plural,
                0),
            NEA('-1',
                '-1 ' + singular,
                -1),
            NEA('-2',
                '-2 ' + plural,
                -2),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT #
                actual = test_object.of(case.actual)
                # ASSERT #
                self.assertEqual(case.expected,
                                 actual)


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
                                                                    'the-plural'),
                                                 '[',
                                                 ']')

        self.assertEqual('det-word',
                         value.determinator_word,
                         'determinator word')

        self.assertEqual('sing',
                         value.singular,
                         'singular')

        self.assertEqual('the-plural',
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
        cases = [
            Case(
                'flags: none',
                '',
                expected=' '.join([name.determinator_word,
                                   name.singular])
            ),
            Case(
                'flags: quoted',
                SC.FLAG_SEPARATOR + SC.QUOTED_FLAG,
                expected=' '.join([name.determinator_word,
                                   ''.join([name.quoting_begin,
                                            name.singular,
                                            name.quoting_end])])
            ),
            Case(
                'flags:init_cap',
                SC.FLAG_SEPARATOR + SC.INIT_CAP_FLAG,
                expected=' '.join([name.determinator_word.capitalize(),
                                   name.singular])
            ),
            Case(
                'flags:upper',
                SC.FLAG_SEPARATOR + SC.UPPER_CASE_FLAG,
                expected=' '.join([name.determinator_word.upper(),
                                   name.singular.upper()])
            ),
            Case(
                'flags:upper quoted',
                SC.FLAG_SEPARATOR +
                SC.UPPER_CASE_FLAG +
                SC.QUOTED_FLAG,
                expected=' '.join([name.determinator_word.upper(),
                                   ''.join([name.quoting_begin,
                                            name.singular.upper(),
                                            name.quoting_end])])
            ),
            Case(
                'flags:quoted upper',
                SC.FLAG_SEPARATOR +
                SC.QUOTED_FLAG +
                SC.UPPER_CASE_FLAG,
                expected=' '.join([name.determinator_word.upper(),
                                   ''.join([name.quoting_begin,
                                            name.singular.upper(),
                                            name.quoting_end])])
            ),
        ]

        for case in cases:
            format_tail = ':' + SC.DETERMINED + case.format_string
            with self.subTest(name=case.name,
                              format_string=case.format_string,
                              format_tail=format_tail):
                string_to_format = '{{x{format_string}}}'.format(format_string=format_tail)
                actual = string_to_format.format(x=name)

            self.assertEqual(case.expected, actual)

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
