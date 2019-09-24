import unittest

from exactly_lib.util.simple_textstruct import structure as s
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.util.simple_textstruct.file_printer_output.test_resources import check_minor_block, \
    MINOR_BLOCK_INDENT, LINE_ELEMENT_INDENT, check_minor_blocks, MINOR_BLOCKS_SEPARATOR


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
                s.PLAIN_ELEMENT_PROPERTIES,
            ),
            NameAndValue(
                'indent properties',
                s.INDENTED_ELEMENT_PROPERTIES,
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
                        s.INDENTED_ELEMENT_PROPERTIES,
                    )
                ],
                    s.INDENTED_ELEMENT_PROPERTIES,
                ),
            ),
            NEA(
                'PreFormattedLine, without ending new-line',
                single_line_string + '\n',
                s.MinorBlock([
                    s.LineElement(
                        s.PreFormattedStringLineObject(single_line_string, False),
                        s.INDENTED_ELEMENT_PROPERTIES,
                    )
                ],
                    s.INDENTED_ELEMENT_PROPERTIES,
                ),
            ),
            NEA(
                'PreFormattedLine, with ending new-line',
                single_line_string + '\n',
                s.MinorBlock([
                    s.LineElement(
                        s.PreFormattedStringLineObject(single_line_string + '\n', True),
                        s.INDENTED_ELEMENT_PROPERTIES,
                    )
                ],
                    s.INDENTED_ELEMENT_PROPERTIES,
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
                        s.INDENTED_ELEMENT_PROPERTIES,
                    )
                ],
                    s.INDENTED_ELEMENT_PROPERTIES,
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
        cases = [
            NEA(
                'multiple types, with plain block properties',
                lines_content([
                    string_1,
                    LINE_ELEMENT_INDENT + string_2,
                    string_3,
                ]),
                s.MinorBlock([
                    s.LineElement(
                        s.StringLineObject(string_1),
                        s.PLAIN_ELEMENT_PROPERTIES,
                    ),
                    s.LineElement(
                        s.StringLineObject(string_2),
                        s.INDENTED_ELEMENT_PROPERTIES,
                    ),
                    s.LineElement(
                        s.PreFormattedStringLineObject(string_3, False),
                        s.INDENTED_ELEMENT_PROPERTIES,
                    ),
                ],
                    s.PLAIN_ELEMENT_PROPERTIES,
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
                        s.PLAIN_ELEMENT_PROPERTIES,
                    ),
                    s.LineElement(
                        s.StringLineObject(string_2),
                        s.INDENTED_ELEMENT_PROPERTIES,
                    ),
                    s.LineElement(
                        s.PreFormattedStringLineObject(string_3, False),
                        s.INDENTED_ELEMENT_PROPERTIES,
                    ),
                ],
                    s.INDENTED_ELEMENT_PROPERTIES,
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


class TestMinorBlocks(unittest.TestCase):
    def test_empty_blocks_SHOULD_BE_separated_by_single_block_separator(self):
        # Have not implemented filtering of non-empty blocks.
        # Reason is that such blocks should not be constructed.
        # But implement it if it appears to be useful for making
        # construction easier.

        # ARRANGE #
        string_1 = 'the 1st string'
        empty_block = s.MinorBlock([], s.PLAIN_ELEMENT_PROPERTIES, )
        non_empty_block = s.MinorBlock(
            [
                s.LineElement(
                    s.StringLineObject(string_1), s.PLAIN_ELEMENT_PROPERTIES,
                ),
            ],
            s.PLAIN_ELEMENT_PROPERTIES,
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
                            s.PLAIN_ELEMENT_PROPERTIES,
                        ),
                    ],
                        s.PLAIN_ELEMENT_PROPERTIES,
                    ),
                    s.MinorBlock([
                        s.LineElement(
                            s.StringLineObject(string_2),
                            s.INDENTED_ELEMENT_PROPERTIES,
                        ),
                    ],
                        s.INDENTED_ELEMENT_PROPERTIES,
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
