import unittest

from exactly_lib.util.simple_textstruct import structure as s
from exactly_lib.util.simple_textstruct.structure import TEXT_STYLE__NEUTRAL, ElementProperties, Indentation
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.util.simple_textstruct.file_printer_output.test_resources import check_minor_block, \
    MINOR_BLOCK_INDENT, LINE_ELEMENT_INDENT, check_minor_blocks, MINOR_BLOCKS_SEPARATOR, indentation_cases, \
    single_line_element_w_plain_properties, LAYOUT_SETTINGS


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMinorBlock),
        unittest.makeSuite(TestMinorBlocks),
    ])


class TestMinorBlock(unittest.TestCase):
    def test_empty_block(self):
        expected_output = ''

        cases = [
            NameAndValue(
                'plain properties',
                s.ELEMENT_PROPERTIES__NEUTRAL,
            ),
            NameAndValue(
                'indent properties',
                s.ELEMENT_PROPERTIES__INDENTED,
            ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_minor_block(
                    self,
                    s.MinorBlock([], case.value),
                    expected_output,
                )

    def test_single_line__different_line_object_types_SHOULD_be_handled(self):
        # ARRANGE #
        single_line_string = 'the string'
        single_line_string_2 = 'the other string'

        cases = [
            NEA(
                'StringLine',
                MINOR_BLOCK_INDENT + LINE_ELEMENT_INDENT + single_line_string + '\n',
                s.MinorBlock([
                    s.LineElement(
                        s.StringLineObject(single_line_string),
                        s.ELEMENT_PROPERTIES__INDENTED,
                    )
                ],
                    s.ELEMENT_PROPERTIES__INDENTED,
                ),
            ),
            NEA(
                'PreFormattedLine, without ending new-line',
                single_line_string + '\n',
                s.MinorBlock([
                    s.LineElement(
                        s.PreFormattedStringLineObject(single_line_string, False),
                        s.ELEMENT_PROPERTIES__INDENTED,
                    )
                ],
                    s.ELEMENT_PROPERTIES__INDENTED,
                ),
            ),
            NEA(
                'PreFormattedLine, with ending new-line',
                single_line_string + '\n',
                s.MinorBlock([
                    s.LineElement(
                        s.PreFormattedStringLineObject(single_line_string + '\n', True),
                        s.ELEMENT_PROPERTIES__INDENTED,
                    )
                ],
                    s.ELEMENT_PROPERTIES__INDENTED,
                ),
            ),
            NEA(
                'StringLines',
                lines_content([
                    MINOR_BLOCK_INDENT + LINE_ELEMENT_INDENT + single_line_string,
                    MINOR_BLOCK_INDENT + LINE_ELEMENT_INDENT + single_line_string_2,
                ]),
                s.MinorBlock([
                    s.LineElement(
                        s.StringLinesObject([single_line_string,
                                             single_line_string_2]),
                        s.ELEMENT_PROPERTIES__INDENTED,
                    )
                ],
                    s.ELEMENT_PROPERTIES__INDENTED,
                ),
            ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_minor_block(
                    self,
                    case.actual,
                    case.expected,
                )

    def test_multiple_line_elements(self):
        # ARRANGE #
        string_1 = 'the 1st string'
        string_2 = 'the 2nd string'
        string_3 = 'the 3rd string'
        string_4 = 'the 4th string'
        cases = [
            NEA(
                'multiple types, with plain block properties',
                lines_content([
                    string_1,
                    LINE_ELEMENT_INDENT + LINE_ELEMENT_INDENT + string_2,
                    LINE_ELEMENT_INDENT + string_3,
                    string_4,
                ]),
                s.MinorBlock([
                    s.LineElement(
                        s.StringLineObject(string_1),
                        s.ELEMENT_PROPERTIES__NEUTRAL,
                    ),
                    s.LineElement(
                        s.StringLineObject(string_2),
                        s.indentation_properties(2),
                    ),
                    s.LineElement(
                        s.StringLineObject(string_3),
                        s.indentation_properties(1),
                    ),
                    s.LineElement(
                        s.PreFormattedStringLineObject(string_4, False),
                        s.ELEMENT_PROPERTIES__INDENTED,
                    ),
                ],
                    s.ELEMENT_PROPERTIES__NEUTRAL,
                ),
            ),
            NEA(
                'multiple types, with indent block properties',
                lines_content([
                    MINOR_BLOCK_INDENT + string_1,
                    MINOR_BLOCK_INDENT + LINE_ELEMENT_INDENT + string_2,
                    string_3,
                ]),
                s.MinorBlock([
                    s.LineElement(
                        s.StringLineObject(string_1),
                        s.ELEMENT_PROPERTIES__NEUTRAL,
                    ),
                    s.LineElement(
                        s.StringLineObject(string_2),
                        s.ELEMENT_PROPERTIES__INDENTED,
                    ),
                    s.LineElement(
                        s.PreFormattedStringLineObject(string_3, False),
                        s.ELEMENT_PROPERTIES__INDENTED,
                    ),
                ],
                    s.ELEMENT_PROPERTIES__INDENTED,
                ),
            ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_minor_block(
                    self,
                    case.actual,
                    case.expected,
                )

    def test_indentation_element_property_SHOULD_cause_indentation(self):
        # ARRANGE #
        line_object = s.StringLineObject('the string')
        for case in _INDENTATION_CASES:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_minor_block(
                    self,
                    to_render=
                    s.MinorBlock(
                        [
                            s.LineElement(line_object)
                        ],
                        ElementProperties(case.actual,
                                          TEXT_STYLE__NEUTRAL),
                    ),
                    expectation=
                    lines_content(
                        [
                            case.expected + line_object.string
                        ]
                    ),
                )

    def test_indentation_element_properties_SHOULD_be_accumulated(self):
        # ARRANGE #

        line_object = s.StringLineObject('the string')
        block_properties = ElementProperties(
            Indentation(2, '<block indent suffix>'),
            TEXT_STYLE__NEUTRAL,
        )
        line_element_properties = ElementProperties(
            Indentation(3, '<line element indent suffix>'),
            TEXT_STYLE__NEUTRAL,
        )

        # ACT & ASSERT #

        check_minor_block(
            self,
            to_render=
            s.MinorBlock(
                [
                    s.LineElement(line_object, line_element_properties)
                ],
                block_properties,
            ),
            expectation=
            lines_content(
                [
                    (
                            (LAYOUT_SETTINGS.minor_block.indent * block_properties.indentation.level) +
                            block_properties.indentation.suffix +
                            (LAYOUT_SETTINGS.line_element_indent * line_element_properties.indentation.level) +
                            line_element_properties.indentation.suffix +
                            line_object.string
                    )

                ]
            ),
        )


class TestMinorBlocks(unittest.TestCase):
    def test_empty_blocks_SHOULD_BE_separated_by_single_block_separator(self):
        # Have not implemented filtering of non-empty blocks.
        # Reason is that such blocks should not be constructed.
        # But implement it if it appears to be useful for making
        # construction easier.

        # ARRANGE #
        string_1 = 'the 1st string'
        empty_block = s.MinorBlock([], s.ELEMENT_PROPERTIES__NEUTRAL, )
        non_empty_block = s.MinorBlock(
            [
                s.LineElement(
                    s.StringLineObject(string_1), s.ELEMENT_PROPERTIES__NEUTRAL,
                ),
            ],
            s.ELEMENT_PROPERTIES__NEUTRAL,
        )
        cases = [
            NEA(
                'two empty blocks',
                lines_content([
                    MINOR_BLOCKS_SEPARATOR,
                ]),
                [
                    empty_block,
                    empty_block,
                ],
            ),
            NEA(
                'first non-empty, second empty',
                lines_content([
                    string_1,
                    MINOR_BLOCKS_SEPARATOR,
                ]),
                [
                    non_empty_block,
                    empty_block,
                ],
            ),
            NEA(
                'first non-empty, second empty',
                lines_content([
                    string_1,
                    MINOR_BLOCKS_SEPARATOR,
                ]),
                [
                    non_empty_block,
                    empty_block,
                ],
            ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_minor_blocks(
                    self,
                    case.actual,
                    case.expected,
                )

    def test_non_empty_blocks_SHOULD_BE_separated_by_single_block_separator(self):
        # ARRANGE #
        string_1 = 'the 1st string'
        string_2 = 'the 2nd string'
        cases = [
            NEA(
                'two blocks, with different indent properties',
                lines_content([
                    string_1,
                    MINOR_BLOCKS_SEPARATOR,
                    MINOR_BLOCK_INDENT + LINE_ELEMENT_INDENT + string_2,
                ]),
                [
                    s.MinorBlock([
                        s.LineElement(
                            s.StringLineObject(string_1),
                            s.ELEMENT_PROPERTIES__NEUTRAL,
                        ),
                    ],
                        s.ELEMENT_PROPERTIES__NEUTRAL,
                    ),
                    s.MinorBlock([
                        s.LineElement(
                            s.StringLineObject(string_2),
                            s.ELEMENT_PROPERTIES__INDENTED,
                        ),
                    ],
                        s.ELEMENT_PROPERTIES__INDENTED,
                    ),
                ],
            ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_minor_blocks(
                    self,
                    case.actual,
                    case.expected,
                )

    def test_indentation_SHOULD_BE_applied_per_block(self):
        # ARRANGE #
        string_1 = 'the 1st string'
        string_2 = 'the 2nd string'
        cases = [
            NEA(
                'two blocks, with different indent properties',
                lines_content([
                    MINOR_BLOCK_INDENT + MINOR_BLOCK_INDENT + string_1,
                    MINOR_BLOCKS_SEPARATOR,
                    string_2,
                ]),
                [
                    s.MinorBlock([
                        single_line_element_w_plain_properties(string_1),
                    ],
                        s.indentation_properties(2),
                    ),
                    s.MinorBlock([
                        single_line_element_w_plain_properties(string_2),
                    ],
                        s.ELEMENT_PROPERTIES__NEUTRAL,
                    ),
                ],
            ),
        ]

        for case in cases:
            # ACT & ASSERT #
            check_minor_blocks(
                self,
                case.actual,
                case.expected,
            )


_INDENTATION_CASES = indentation_cases(MINOR_BLOCK_INDENT)
