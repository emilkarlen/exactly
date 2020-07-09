import unittest
from typing import Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.simple_textstruct import structure as s
from exactly_lib.util.simple_textstruct.structure import TEXT_STYLE__NEUTRAL, ElementProperties, Indentation
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.util.simple_textstruct.file_printer_output.test_resources import MINOR_BLOCK_INDENT, \
    LINE_ELEMENT_INDENT, MINOR_BLOCKS_SEPARATOR, check_major_block, \
    MAJOR_BLOCK_INDENT, MAJOR_BLOCKS_SEPARATOR, check_major_blocks, check_document, indentation_cases, \
    single_line_element_w_plain_properties, LAYOUT_SETTINGS


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMajorBlock),
        unittest.makeSuite(TestMajorBlocksAndDocument),
    ])


class TestMajorBlock(unittest.TestCase):
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
                check_major_block(
                    self,
                    s.MajorBlock([], case.value),
                    expected_output,
                )

    def test_single_line__different_line_object_types_SHOULD_be_handled(self):
        # ARRANGE #
        single_line_string = 'the string'
        single_line_string_2 = 'the other string'

        cases = [
            NEA(
                'StringLine',
                MAJOR_BLOCK_INDENT + MINOR_BLOCK_INDENT + LINE_ELEMENT_INDENT + single_line_string + '\n',
                s.MajorBlock([
                    s.MinorBlock([
                        s.LineElement(
                            s.StringLineObject(single_line_string),
                            s.ELEMENT_PROPERTIES__INDENTED,
                        )
                    ],
                        s.ELEMENT_PROPERTIES__INDENTED,
                    ),
                ],
                    s.ELEMENT_PROPERTIES__INDENTED,
                ),
            ),
            NEA(
                'PreFormattedLine, without ending new-line',
                single_line_string + '\n',
                s.MajorBlock([
                    s.MinorBlock([
                        s.LineElement(
                            s.PreFormattedStringLineObject(single_line_string, False),
                            s.ELEMENT_PROPERTIES__INDENTED,
                        )
                    ],
                        s.ELEMENT_PROPERTIES__INDENTED,
                    )
                ],
                    s.ELEMENT_PROPERTIES__INDENTED,
                ),
            ),
            NEA(
                'StringLines',
                lines_content([
                    MAJOR_BLOCK_INDENT + MINOR_BLOCK_INDENT + LINE_ELEMENT_INDENT + single_line_string,
                    MAJOR_BLOCK_INDENT + MINOR_BLOCK_INDENT + LINE_ELEMENT_INDENT + single_line_string_2,
                ]),
                s.MajorBlock([
                    s.MinorBlock([
                        s.LineElement(
                            s.StringLinesObject([single_line_string,
                                                 single_line_string_2]),
                            s.ELEMENT_PROPERTIES__INDENTED,
                        )
                    ],
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
                check_major_block(
                    self,
                    case.actual,
                    case.expected,
                )

    def test_multiple_minor_blocks(self):
        # ARRANGE #
        string_1 = 'the 1st string'
        string_2 = 'the 2nd string'
        string_3 = 'the 3rd string'
        cases = [
            NEA(
                'multiple types, with different indent properties',
                lines_content([
                    MAJOR_BLOCK_INDENT + string_1,
                    MINOR_BLOCKS_SEPARATOR,
                    MAJOR_BLOCK_INDENT + MINOR_BLOCK_INDENT + LINE_ELEMENT_INDENT + string_2,
                    MINOR_BLOCKS_SEPARATOR,
                    string_3,
                ]),
                s.MajorBlock([
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
                    s.MinorBlock([
                        s.LineElement(
                            s.PreFormattedStringLineObject(string_3, False),
                            s.ELEMENT_PROPERTIES__INDENTED,
                        ),
                    ],
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
                check_major_block(
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
                check_major_block(
                    self,
                    to_render=
                    s.MajorBlock([
                        s.MinorBlock([s.LineElement(line_object)], s.ELEMENT_PROPERTIES__NEUTRAL)
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
        major_block_properties = ElementProperties(
            Indentation(2, '<major block indent suffix>'),
            TEXT_STYLE__NEUTRAL,
        )
        minor_block_properties = ElementProperties(
            Indentation(3, '<minor block indent suffix>'),
            TEXT_STYLE__NEUTRAL,
        )
        line_element_properties = ElementProperties(
            Indentation(4, '<line element indent suffix>'),
            TEXT_STYLE__NEUTRAL,
        )

        # ACT & ASSERT #

        check_major_block(
            self,
            to_render=
            s.MajorBlock([
                s.MinorBlock(
                    [s.LineElement(line_object,
                                   line_element_properties)],
                    minor_block_properties)
            ],
                major_block_properties,
            ),
            expectation=
            lines_content(
                [
                    (
                            (LAYOUT_SETTINGS.major_block.indent * major_block_properties.indentation.level) +
                            major_block_properties.indentation.suffix +
                            (LAYOUT_SETTINGS.minor_block.indent * minor_block_properties.indentation.level) +
                            minor_block_properties.indentation.suffix +
                            (LAYOUT_SETTINGS.line_element_indent * line_element_properties.indentation.level) +
                            line_element_properties.indentation.suffix +
                            line_object.string
                    )

                ]
            ),
        )


class TestMajorBlocksAndDocument(unittest.TestCase):
    def test_empty_blocks_SHOULD_BE_separated_by_single_block_separator(self):
        # Have not implemented filtering of non-empty blocks.
        # Reason is that such blocks should not be constructed.
        # But implement it if it appears to be useful for making
        # construction easier.

        # ARRANGE #
        string_1 = 'the 1st string'

        empty_block = s.MajorBlock([
            s.MinorBlock([],
                         s.ELEMENT_PROPERTIES__NEUTRAL,
                         ),
        ],
            s.ELEMENT_PROPERTIES__NEUTRAL
        )

        non_empty_block = s.MajorBlock([
            single_line_minor_block_w_plain_properties(string_1),
        ],
            s.ELEMENT_PROPERTIES__NEUTRAL,
        )
        cases = [
            NEA(
                'two empty blocks',
                lines_content([
                    MAJOR_BLOCKS_SEPARATOR,
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
                    MAJOR_BLOCKS_SEPARATOR,
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
                    MAJOR_BLOCKS_SEPARATOR,
                ]),
                [
                    non_empty_block,
                    empty_block,
                ],
            ),
        ]

        for case in cases:
            check_block_sequence_and_document(self, case)

    def test_non_empty_blocks_SHOULD_BE_separated_by_single_block_separator(self):
        # ARRANGE #
        string_1 = 'the 1st string'
        string_2 = 'the 2nd string'
        cases = [
            NEA(
                'two blocks, with different indent properties',
                lines_content([
                    string_1,
                    MAJOR_BLOCKS_SEPARATOR,
                    MAJOR_BLOCK_INDENT + MINOR_BLOCK_INDENT + LINE_ELEMENT_INDENT + string_2,
                ]),
                [
                    s.MajorBlock([
                        single_line_minor_block_w_plain_properties(string_1),
                    ],
                        s.ELEMENT_PROPERTIES__NEUTRAL,
                    ),
                    s.MajorBlock([
                        s.MinorBlock([
                            s.LineElement(
                                s.StringLineObject(string_2),
                                s.ELEMENT_PROPERTIES__INDENTED,
                            ),
                        ],
                            s.ELEMENT_PROPERTIES__INDENTED,
                        ),
                    ],
                        s.ELEMENT_PROPERTIES__INDENTED,
                    ),
                ],
            ),
        ]

        for case in cases:
            check_block_sequence_and_document(self, case)

    def test_indentation_SHOULD_BE_applied_per_block(self):
        # ARRANGE #
        string_1 = 'the 1st string'
        string_2 = 'the 2nd string'
        cases = [
            NEA(
                'two blocks, with different indent properties',
                lines_content([
                    MAJOR_BLOCK_INDENT + MAJOR_BLOCK_INDENT + string_1,
                    MAJOR_BLOCKS_SEPARATOR,
                    string_2,
                ]),
                [
                    s.MajorBlock([
                        single_line_minor_block_w_plain_properties(string_1),
                    ],
                        s.indentation_properties(2),
                    ),
                    s.MajorBlock([
                        single_line_minor_block_w_plain_properties(string_2),
                    ],
                        s.ELEMENT_PROPERTIES__NEUTRAL,
                    ),
                ],
            ),
        ]

        for case in cases:
            check_block_sequence_and_document(self, case)


def check_block_sequence_and_document(put: unittest.TestCase,
                                      case: NEA[str, Sequence[s.MajorBlock]],
                                      ):
    with put.subTest(case.name,
                     type='MajorBlock:s'):
        # ACT & ASSERT #
        check_major_blocks(
            put,
            case.actual,
            case.expected,
        )
    with put.subTest(case.name,
                     type='Document'):
        # ACT & ASSERT #
        check_document(
            put,
            s.Document(case.actual),
            case.expected,
        )


def single_line_minor_block_w_plain_properties(line_contents: str) -> s.MinorBlock:
    return s.MinorBlock([
        single_line_element_w_plain_properties(line_contents),
    ],
        s.ELEMENT_PROPERTIES__NEUTRAL,
    )


_INDENTATION_CASES = indentation_cases(MAJOR_BLOCK_INDENT)
