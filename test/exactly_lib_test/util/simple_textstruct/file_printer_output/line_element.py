import unittest

from exactly_lib.util.ansi_terminal_color import ForegroundColor, FontStyle
from exactly_lib.util.simple_textstruct import structure as s
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.util.simple_textstruct.file_printer_output.test_resources import LINE_ELEMENT_INDENT, \
    check_line_element


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestLineElementOfPreFormattedString),
        unittest.makeSuite(TestLineElementOfStringLine),
        unittest.makeSuite(TestLineElementOfStringLines),
    ])


class TestLineElementOfPreFormattedString(unittest.TestCase):
    single_line_string = 'the string'
    multi_line_string = 'the first line\nthe second line'
    cases = [
        NEA(
            'single line, no ending new line',
            single_line_string + '\n',
            s.PreFormattedStringLineObject(
                single_line_string,
                False,
            ),
        ),
        NEA(
            'single line, with ending new line',
            single_line_string + '\n',
            s.PreFormattedStringLineObject(
                single_line_string + '\n',
                True,
            ),
        ),
        NEA(
            'multiple lines, no ending new line',
            multi_line_string + '\n',
            s.PreFormattedStringLineObject(
                multi_line_string + '\n',
                True,
            ),
        ),
    ]

    def test_with_plain_element_properties(self):
        # ARRANGE #
        element_properties = s.PLAIN_ELEMENT_PROPERTIES

        for case in self.cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_line_element(
                    self,
                    s.LineElement(case.actual, element_properties),
                    case.expected,
                )

    def test_element_properties_SHOULD_be_ignored(self):
        # ARRANGE #
        ep_with_indent = s.ElementProperties(True,
                                             ForegroundColor.BLUE,
                                             FontStyle.UNDERLINE)

        for case in self.cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_line_element(
                    self,
                    s.LineElement(case.actual, ep_with_indent),
                    case.expected,
                )


class TestLineElementOfStringLine(unittest.TestCase):
    single_line_string = 'the string'
    multi_line_string = 'the first line\nthe second line'
    cases = [
        NEA(
            'single line, no ending new line',
            single_line_string + '\n',
            s.StringLineObject(
                single_line_string,
                False,
            ),
        ),
        NEA(
            'single line, with ending new line',
            single_line_string + '\n',
            s.StringLineObject(
                single_line_string + '\n',
                True,
            ),
        ),
        NEA(
            'multiple lines, no ending new line',
            multi_line_string + '\n',
            s.StringLineObject(
                multi_line_string + '\n',
                True,
            ),
        ),
    ]

    def test_with_plain_element_properties(self):
        # ARRANGE #
        element_properties = s.PLAIN_ELEMENT_PROPERTIES

        for case in self.cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_line_element(
                    self,
                    s.LineElement(case.actual, element_properties),
                    case.expected,
                )

    def test_WHEN_indentation_element_property_is_true_THEN_rendition_SHOULD_be_indented(self):
        # ARRANGE #
        ep_with_indent = s.INDENTED_ELEMENT_PROPERTIES

        for case in self.cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_line_element(
                    self,
                    s.LineElement(case.actual, ep_with_indent),
                    LINE_ELEMENT_INDENT + case.expected,
                )


class TestLineElementOfStringLines(unittest.TestCase):
    line_1 = 'the 1st string'
    line_2 = 'the 2nd string'
    multi_line_string = 'the first line\nthe second line'
    cases = [
        NEA(
            'no lines',
            [],
            s.StringLinesObject(
                [],
            ),
        ),
        NEA(
            'single line',
            [line_1],
            s.StringLinesObject(
                [line_1],
            ),
        ),
        NEA(
            'multiple lines',
            [line_1, line_2],
            s.StringLinesObject(
                [line_1, line_2],
            ),
        ),
        NEA(
            'multiple lines, one with an embedded new-line',
            [line_1, multi_line_string],
            s.StringLinesObject(
                [line_1, multi_line_string],
            ),
        ),
    ]

    def test_with_plain_element_properties(self):
        # ARRANGE #
        element_properties = s.PLAIN_ELEMENT_PROPERTIES

        for case in self.cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_line_element(
                    self,
                    s.LineElement(case.actual, element_properties),
                    lines_content(case.expected),
                )

    def test_WHEN_indentation_element_property_is_true_THEN_rendition_SHOULD_be_indented(self):
        # ARRANGE #
        element_properties = s.INDENTED_ELEMENT_PROPERTIES

        for case in self.cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_line_element(
                    self,
                    s.LineElement(case.actual, element_properties),
                    lines_content(
                        [
                            LINE_ELEMENT_INDENT + l
                            for l in case.expected
                        ]
                    ),
                )
