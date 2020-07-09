import unittest

from exactly_lib.util.ansi_terminal_color import ForegroundColor, FontStyle
from exactly_lib.util.simple_textstruct import structure as s
from exactly_lib.util.simple_textstruct.structure import Indentation, TextStyle, ElementProperties, TEXT_STYLE__NEUTRAL
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.util.simple_textstruct.file_printer_output.test_resources import LINE_ELEMENT_INDENT, \
    check_line_element, indentation_cases, FilePrinterWithTextPropertiesForTest


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestLineElementOfPreFormattedString),
        unittest.makeSuite(TestLineElementOfStringLine),
        unittest.makeSuite(TestLineElementOfStringLines),
        unittest.makeSuite(TestElementProperties),
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
        element_properties = s.ELEMENT_PROPERTIES__NEUTRAL

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
        ep_with_indent = s.ElementProperties(Indentation(1),
                                             TextStyle(color=ForegroundColor.BLUE,
                                                       font_style=FontStyle.UNDERLINE),
                                             )

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
        element_properties = s.ELEMENT_PROPERTIES__NEUTRAL

        for case in self.cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_line_element(
                    self,
                    s.LineElement(case.actual, element_properties),
                    case.expected,
                )

    def test_indentation_element_property_SHOULD_cause_indentation(self):
        # ARRANGE #
        for indentation_case in _INDENTATION_CASES:
            for case in self.cases:
                with self.subTest(line_object=case.name,
                                  indentation=indentation_case.name):
                    # ACT & ASSERT #
                    check_line_element(
                        self,
                        s.LineElement(case.actual,
                                      ElementProperties(indentation_case.actual,
                                                        TEXT_STYLE__NEUTRAL)),
                        indentation_case.expected + case.expected,
                    )


class TestElementProperties(unittest.TestCase):
    def test_color_SHOULD_cause_text_to_be_surrounded_by_color_codes(self):
        # ARRANGE #
        text_color = ForegroundColor.BLUE
        line_object = s.StringLineObject('line object text',
                                         string_is_line_ended=False)
        # ACT & ASSERT #
        check_line_element(
            self,
            s.LineElement(line_object,
                          ElementProperties(s.INDENTATION__NEUTRAL,
                                            TextStyle(text_color))),
            ''.join([
                FilePrinterWithTextPropertiesForTest.color_string_for(text_color),
                line_object.string,
                '\n',
                FilePrinterWithTextPropertiesForTest.UNSET_COLOR,
            ]),
        )

    def test_font_style_SHOULD_cause_text_to_be_surrounded_by_style_codes(self):
        # ARRANGE #
        font_style = FontStyle.BOLD
        line_object = s.StringLineObject('line object text',
                                         string_is_line_ended=False)
        # ACT & ASSERT #
        check_line_element(
            self,
            s.LineElement(line_object,
                          ElementProperties(s.INDENTATION__NEUTRAL,
                                            TextStyle(font_style=font_style))),
            ''.join([
                FilePrinterWithTextPropertiesForTest.font_style_string_for(font_style),
                line_object.string,
                '\n',
                FilePrinterWithTextPropertiesForTest.UNSET_FONT_STYLE,
            ]),
        )

    def test_color_and_font_style_SHOULD_cause_text_to_be_surrounded_by_color_and_style_codes(self):
        # ARRANGE #
        text_color = ForegroundColor.BLUE
        font_style = FontStyle.BOLD
        line_object = s.StringLineObject('line object text',
                                         string_is_line_ended=False)
        # ACT & ASSERT #
        check_line_element(
            self,
            s.LineElement(line_object,
                          ElementProperties(s.INDENTATION__NEUTRAL,
                                            TextStyle(color=text_color,
                                                      font_style=font_style))),
            ''.join([
                FilePrinterWithTextPropertiesForTest.font_style_string_for(font_style),
                FilePrinterWithTextPropertiesForTest.color_string_for(text_color),
                line_object.string,
                '\n',
                FilePrinterWithTextPropertiesForTest.UNSET_COLOR,
                FilePrinterWithTextPropertiesForTest.UNSET_FONT_STYLE,
            ]),
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
        element_properties = s.ELEMENT_PROPERTIES__NEUTRAL

        for case in self.cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_line_element(
                    self,
                    s.LineElement(case.actual, element_properties),
                    lines_content(case.expected),
                )

    def test_indentation_element_property_SHOULD_cause_indentation(self):
        # ARRANGE #
        for indentation_case in _INDENTATION_CASES:
            for case in self.cases:
                with self.subTest(line_object=case.name,
                                  indentation=indentation_case.name):
                    # ACT & ASSERT #
                    check_line_element(
                        self,
                        s.LineElement(case.actual,
                                      ElementProperties(indentation_case.actual,
                                                        TEXT_STYLE__NEUTRAL)),
                        lines_content(
                            [
                                indentation_case.expected + l
                                for l in case.expected
                            ]
                        ),
                    )


_INDENTATION_CASES = indentation_cases(LINE_ELEMENT_INDENT)
