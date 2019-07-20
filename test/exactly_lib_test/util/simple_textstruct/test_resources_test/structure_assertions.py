import unittest

from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.simple_textstruct.structure import LineElement, MinorBlock, LineObjectVisitor, ENV, RET, \
    LineObject, PLAIN_ELEMENT_PROPERTIES, ElementProperties, MajorBlock, PreFormattedStringLineObject, StringLineObject, \
    StringLinesObject
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.simple_textstruct.test_resources import structure_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMatchesProperties),
        unittest.makeSuite(TestMatchesLineElement),
        unittest.makeSuite(TestMatchesMinorBlock),
        unittest.makeSuite(TestMatchesMajorBlock),
        unittest.makeSuite(TestIsPreFormattedString),
        unittest.makeSuite(TestIsString),
        unittest.makeSuite(TestIsStringLines),
    ])


class TestMatchesProperties(unittest.TestCase):
    def test_matches(self):
        cases = [
            NEA('default',
                expected=
                sut.matches_element_properties(),
                actual=
                ElementProperties(True, None),
                ),
            NEA('indented',
                expected=
                sut.matches_element_properties(
                    indented=asrt.equals(True),
                ),
                actual=
                ElementProperties(True, None),
                ),
            NEA('color',
                expected=
                sut.matches_element_properties(
                    color=asrt.equals(ForegroundColor.GREEN),
                ),
                actual=
                ElementProperties(True, ForegroundColor.GREEN),
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                case.expected.apply_without_message(self, case.actual)

    def test_not_matches(self):
        cases = [
            NEA('unexpected indent',
                expected=
                sut.matches_element_properties(
                    indented=asrt.equals(True),
                ),
                actual=
                ElementProperties(False, None),
                ),
            NEA('unexpected color',
                expected=
                sut.matches_element_properties(
                    color=asrt.equals(ForegroundColor.GREEN),
                ),
                actual=
                ElementProperties(False, ForegroundColor.RED),
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
                            PLAIN_ELEMENT_PROPERTIES),
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
                            PLAIN_ELEMENT_PROPERTIES),
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
                MinorBlock([LineElement(LineObjectForTest())]),
                ),
            NEA('test of element properties',
                expected=
                sut.matches_minor_block(
                    asrt.anything_goes(),
                    properties=sut.matches_element_properties(
                        indented=asrt.is_instance(bool)
                    ),
                ),
                actual=
                MinorBlock([],
                           PLAIN_ELEMENT_PROPERTIES),
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
                                        PLAIN_ELEMENT_PROPERTIES)]),
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
                        indented=asrt.is_instance(bool)
                    ),
                ),
                actual=
                MajorBlock([],
                           PLAIN_ELEMENT_PROPERTIES),
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
                                       PLAIN_ELEMENT_PROPERTIES)]),
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


class LineObjectForTest(LineObject):
    def accept(self, visitor: 'LineObjectVisitor[ENV, RET]', env: ENV) -> RET:
        raise ValueError('should not be used')