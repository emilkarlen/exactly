import unittest

from exactly_lib.util.ansi_terminal_color import ForegroundColor, FontStyle
from exactly_lib.util.simple_textstruct.structure import LineElement, MinorBlock, LineObjectVisitor, ENV, RET, \
    LineObject, ELEMENT_PROPERTIES__NEUTRAL, ElementProperties, MajorBlock, PreFormattedStringLineObject, \
    StringLineObject, \
    StringLinesObject, Indentation, TextStyle, TEXT_STYLE__NEUTRAL, INDENTATION__NEUTRAL
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.simple_textstruct.test_resources import structure_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIndentation),
        unittest.makeSuite(TestMatchesTextStyle),
        unittest.makeSuite(TestMatchesProperties),
        unittest.makeSuite(TestMatchesLineElement),
        unittest.makeSuite(TestMatchesMinorBlock),
        unittest.makeSuite(TestMatchesMajorBlock),
        unittest.makeSuite(TestIsPreFormattedString),
        unittest.makeSuite(TestIsString),
        unittest.makeSuite(TestIsStringLines),
        unittest.makeSuite(TestAnyLineObject),
    ])


class TestMatchesProperties(unittest.TestCase):
    def test_matches(self):
        cases = [
            NEA('default',
                expected=
                sut.matches_element_properties(),
                actual=
                ElementProperties(Indentation(1, ''), TEXT_STYLE__NEUTRAL),
                ),
            NEA('indentation',
                expected=
                sut.matches_element_properties(
                    indentation=sut.matches_indentation(level=asrt.equals(69)),
                ),
                actual=
                ElementProperties(Indentation(69, ''), TEXT_STYLE__NEUTRAL),
                ),
            NEA('text_style',
                expected=
                sut.matches_element_properties(
                    text_style=sut.matches_text_style(color=asrt.equals(ForegroundColor.GREEN)),
                ),
                actual=
                ElementProperties(INDENTATION__NEUTRAL,
                                  TextStyle(ForegroundColor.GREEN, None)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('indentation',
                expected=
                sut.matches_element_properties(
                    indentation=sut.matches_indentation(level=asrt.equals(1)),
                ),
                actual=
                ElementProperties(Indentation(0, ''),
                                  TEXT_STYLE__NEUTRAL),
                ),
            NEA('text_style',
                expected=
                sut.matches_element_properties(
                    text_style=sut.matches_text_style(color=asrt.equals(ForegroundColor.GREEN)),
                ),
                actual=
                ElementProperties(INDENTATION__NEUTRAL,
                                  TextStyle(ForegroundColor.RED, None)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestIndentation(unittest.TestCase):
    def test_matches(self):
        cases = [
            NEA('default',
                expected=
                sut.matches_indentation(),
                actual=
                Indentation(1, 'a suffix'),
                ),
            NEA('level',
                expected=
                sut.matches_indentation(
                    level=asrt.equals(1),
                ),
                actual=
                Indentation(1, ''),
                ),
            NEA('suffix',
                expected=
                sut.matches_indentation(
                    suffix=asrt.equals('a suffix'),
                ),
                actual=
                Indentation(1, 'a suffix'),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('level',
                expected=
                sut.matches_indentation(
                    level=asrt.equals(1),
                ),
                actual=
                Indentation(0, ''),
                ),
            NEA('suffix',
                expected=
                sut.matches_indentation(
                    suffix=asrt.equals('expected'),
                ),
                actual=
                Indentation(0, 'actual'),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestMatchesTextStyle(unittest.TestCase):
    def test_matches(self):
        cases = [
            NEA('default 1',
                expected=
                sut.matches_text_style(),
                actual=
                TextStyle(None, None),
                ),
            NEA('default/w color',
                expected=
                sut.matches_text_style(),
                actual=
                TextStyle(ForegroundColor.GREEN, None),
                ),
            NEA('default/w style',
                expected=
                sut.matches_text_style(),
                actual=
                TextStyle(None, FontStyle.BOLD),
                ),
            NEA('color',
                expected=
                sut.matches_text_style(
                    color=asrt.equals(ForegroundColor.GREEN),
                ),
                actual=
                TextStyle(ForegroundColor.GREEN, None),
                ),
            NEA('font_style',
                expected=
                sut.matches_text_style(
                    font_style=asrt.equals(FontStyle.BOLD),
                ),
                actual=
                TextStyle(None, FontStyle.BOLD),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('color - different values',
                expected=
                sut.matches_text_style(
                    color=asrt.equals(ForegroundColor.GREEN),
                ),
                actual=
                TextStyle(ForegroundColor.RED, None),
                ),
            NEA('color - actual is None',
                expected=
                sut.matches_text_style(
                    color=asrt.equals(ForegroundColor.GREEN),
                ),
                actual=
                TextStyle(None, None),
                ),
            NEA('font_style - different values',
                expected=
                sut.matches_text_style(
                    font_style=asrt.equals(FontStyle.UNDERLINE),
                ),
                actual=
                TextStyle(None, FontStyle.BOLD),
                ),
            NEA('font_style - actual is None',
                expected=
                sut.matches_text_style(
                    font_style=asrt.equals(FontStyle.UNDERLINE),
                ),
                actual=
                TextStyle(None, None),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestMatchesLineElement(unittest.TestCase):
    def test_matches(self):
        cases = [
            NEA('empty list of line elements',
                expected=
                sut.matches_line_element(
                    asrt.is_instance(LineObjectForTest),
                ),
                actual=
                LineElement(LineObjectForTest()),
                ),
            NEA('line object',
                expected=
                sut.matches_line_element(
                    asrt.is_instance(LineObjectForTest)
                ),
                actual=
                LineElement(LineObjectForTest()),
                ),
            NEA('element properties',
                expected=
                sut.matches_line_element(
                    asrt.anything_goes(),
                    properties=asrt.is_instance(ElementProperties),
                ),
                actual=
                LineElement(LineObjectForTest(),
                            ELEMENT_PROPERTIES__NEUTRAL),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('unexpected line object',
                expected=
                sut.matches_line_element(
                    asrt.not_(asrt.is_instance(LineObjectForTest))
                ),
                actual=
                LineElement(LineObjectForTest()),
                ),
            NEA('unexpected element properties',
                expected=
                sut.matches_line_element(
                    asrt.anything_goes(),
                    properties=asrt.not_(asrt.is_instance(ElementProperties))
                ),
                actual=
                LineElement(LineObjectForTest(),
                            ELEMENT_PROPERTIES__NEUTRAL),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestMatchesMinorBlock(unittest.TestCase):
    def test_matches(self):
        cases = [
            NEA('empty list of line elements',
                expected=
                sut.matches_minor_block(
                    asrt.is_empty_sequence
                ),
                actual=
                MinorBlock([]),
                ),
            NEA('non-empty list of line elements',
                expected=
                sut.matches_minor_block(
                    asrt.matches_sequence([asrt.is_instance(LineElement)])
                ),
                actual=
                MinorBlock([LineElement(StringLineObject('the string'))]),
                ),
            NEA('test of element properties',
                expected=
                sut.matches_minor_block(
                    asrt.anything_goes(),
                    properties=sut.matches_element_properties(
                        indentation=sut.matches_indentation(level=asrt.equals(72))
                    ),
                ),
                actual=
                MinorBlock([],
                           ElementProperties(Indentation(72, ''),
                                             TEXT_STYLE__NEUTRAL)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('actual is empty list of line elements',
                expected=
                sut.matches_minor_block(
                    asrt.not_(asrt.is_empty_sequence)
                ),
                actual=
                MinorBlock([]),
                ),
            NEA('actual element is unexpected',
                expected=
                sut.matches_minor_block(
                    asrt.matches_sequence([asrt.not_(asrt.is_instance(LineElement))])
                ),
                actual=
                MinorBlock([LineElement(LineObjectForTest())]),
                ),
            NEA('unexpected element properties',
                expected=
                sut.matches_minor_block(
                    asrt.anything_goes(),
                    properties=asrt.not_(asrt.is_instance(ElementProperties))
                ),
                actual=
                MinorBlock([LineElement(LineObjectForTest(),
                                        ELEMENT_PROPERTIES__NEUTRAL)]),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestMatchesMajorBlock(unittest.TestCase):
    def test_matches(self):
        cases = [
            NEA('empty list of blocks',
                expected=
                sut.matches_major_block(
                    asrt.is_empty_sequence
                ),
                actual=
                MajorBlock([]),
                ),
            NEA('non-empty list of blocks',
                expected=
                sut.matches_major_block(
                    asrt.matches_sequence([asrt.is_instance(MinorBlock)])
                ),
                actual=
                MajorBlock([MinorBlock([])]),
                ),
            NEA('test of element properties',
                expected=
                sut.matches_major_block(
                    asrt.anything_goes(),
                    properties=sut.matches_element_properties(
                        indentation=sut.matches_indentation(level=asrt.equals(72))
                    ),
                ),
                actual=
                MajorBlock([],
                           ElementProperties(Indentation(72, ''),
                                             TEXT_STYLE__NEUTRAL)),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('actual is empty list of line elements',
                expected=
                sut.matches_major_block(
                    asrt.not_(asrt.is_empty_sequence)
                ),
                actual=
                MajorBlock([]),
                ),
            NEA('actual element is unexpected',
                expected=
                sut.matches_major_block(
                    asrt.matches_sequence([asrt.not_(asrt.is_instance(MinorBlock))])
                ),
                actual=
                MajorBlock([MinorBlock([])]),
                ),
            NEA('unexpected element properties',
                expected=
                sut.matches_major_block(
                    asrt.anything_goes(),
                    properties=asrt.not_(asrt.is_instance(ElementProperties))
                ),
                actual=
                MajorBlock([MinorBlock([],
                                       ELEMENT_PROPERTIES__NEUTRAL)]),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestIsPreFormattedString(unittest.TestCase):
    def test_matches(self):
        expected_string = 'expected string'
        cases = [
            NEA('default/False',
                expected=
                sut.is_pre_formatted_string(),
                actual=
                PreFormattedStringLineObject('anything', False),
                ),
            NEA('default/True',
                expected=
                sut.is_pre_formatted_string(),
                actual=
                PreFormattedStringLineObject('anything', True),
                ),
            NEA('string',
                expected=
                sut.is_pre_formatted_string(string=asrt.equals(expected_string)),
                actual=
                PreFormattedStringLineObject(expected_string, True)
                ),
            NEA('string is line ended',
                expected=
                sut.is_pre_formatted_string(string_is_line_ended=asrt.equals(True)),
                actual=
                PreFormattedStringLineObject('anything', True),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('unexpected object type',
                expected=
                sut.is_pre_formatted_string(),
                actual=
                LineObjectForTest(),
                ),
            NEA('string',
                expected=
                sut.is_pre_formatted_string(string=asrt.equals('expected')),
                actual=
                PreFormattedStringLineObject('actual', True),
                ),
            NEA('string is line ended',
                expected=
                sut.is_pre_formatted_string(string_is_line_ended=asrt.equals(True)),
                actual=
                PreFormattedStringLineObject('anything', False),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestIsString(unittest.TestCase):
    def test_matches(self):
        expected_string = 'expected string'
        cases = [
            NEA('default/False',
                expected=
                sut.is_string(),
                actual=
                StringLineObject('anything', False),
                ),
            NEA('default/True',
                expected=
                sut.is_string(),
                actual=
                StringLineObject('anything', True),
                ),
            NEA('string',
                expected=
                sut.is_string(string=asrt.equals(expected_string)),
                actual=
                StringLineObject(expected_string, True)
                ),
            NEA('string is line ended',
                expected=
                sut.is_string(string_is_line_ended=asrt.equals(True)),
                actual=
                StringLineObject('anything', True),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('unexpected object type',
                expected=
                sut.is_string(),
                actual=
                LineObjectForTest(),
                ),
            NEA('string',
                expected=
                sut.is_string(string=asrt.equals('expected')),
                actual=
                StringLineObject('actual', True),
                ),
            NEA('string is line ended',
                expected=
                sut.is_string(string_is_line_ended=asrt.equals(True)),
                actual=
                StringLineObject('anything', False),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestIsStringLines(unittest.TestCase):
    def test_matches(self):
        expected_string = 'expected string'
        cases = [
            NEA('default/empty list of lines',
                expected=
                sut.is_string_lines(),
                actual=
                StringLinesObject([]),
                ),
            NEA('default/non-empty list of lines',
                expected=
                sut.is_string_lines(),
                actual=
                StringLinesObject(['a string']),
                ),
            NEA('strings',
                expected=
                sut.is_string_lines(asrt.matches_sequence([asrt.equals(expected_string)])),
                actual=
                StringLinesObject([expected_string])
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('unexpected object type',
                expected=
                sut.is_string_lines(),
                actual=
                LineObjectForTest(),
                ),
            NEA('strings',
                expected=
                sut.is_string_lines(asrt.matches_sequence([asrt.equals('expected')])),
                actual=
                StringLinesObject(['actual']),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(case.expected, case.actual)


class TestAnyLineObject(unittest.TestCase):
    def test_matches(self):
        cases = [
            StringLineObject('s', False),
            StringLinesObject(['a string']),
            PreFormattedStringLineObject('pre-formatted', True),
        ]
        for line_object in cases:
            with self.subTest(str(type(line_object))):
                sut.is_any_line_object().apply_without_message(self, line_object)

    def test_not_matches(self):
        cases = [
            NameAndValue('not a sub class of LineObject',
                         'not a LineObject'
                         ),
            NameAndValue('Unknown sub class of LineObject',
                         LineObjectForTest()
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assert_that_assertion_fails(sut.is_any_line_object(), case.value)


class LineObjectForTest(LineObject):
    def accept(self, visitor: 'LineObjectVisitor[ENV, RET]', env: ENV) -> RET:
        raise ValueError('should not be used')
