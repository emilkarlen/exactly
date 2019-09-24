import unittest
from typing import Sequence

from exactly_lib.util.simple_textstruct import structure as s
from exactly_lib.util.string import lines_content
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.util.simple_textstruct.file_printer_output.test_resources import MINOR_BLOCK_INDENT, \
    LINE_ELEMENT_INDENT, MINOR_BLOCKS_SEPARATOR, check_major_block, \
    MAJOR_BLOCK_INDENT, MAJOR_BLOCKS_SEPARATOR, check_major_blocks, check_document


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
                            s.INDENTED_ELEMENT_PROPERTIES,
                        )
                    ],
                        s.INDENTED_ELEMENT_PROPERTIES,
                    ),
                ],
                    s.INDENTED_ELEMENT_PROPERTIES,
                ),
            ),
            NEA(
                'PreFormattedLine, without ending new-line',
                single_line_string + '\n',
                s.MajorBlock([
                    s.MinorBlock([
                        s.LineElement(
                            s.PreFormattedStringLineObject(single_line_string, False),
                            s.INDENTED_ELEMENT_PROPERTIES,
                        )
                    ],
                        s.INDENTED_ELEMENT_PROPERTIES,
                    )
                ],
                    s.INDENTED_ELEMENT_PROPERTIES,
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
                            s.INDENTED_ELEMENT_PROPERTIES,
                        )
                    ],
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
                    s.MinorBlock([
                        s.LineElement(
                            s.PreFormattedStringLineObject(string_3, False),
                            s.INDENTED_ELEMENT_PROPERTIES,
                        ),
                    ],
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
                check_major_block(
                    self,
                    case.actual,
                    case.expected,
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
                         s.PLAIN_ELEMENT_PROPERTIES,
                         ),
        ],
            s.PLAIN_ELEMENT_PROPERTIES
        )

        non_empty_block = s.MajorBlock([
            s.MinorBlock([
                s.LineElement(
                    s.StringLineObject(string_1),
                    s.PLAIN_ELEMENT_PROPERTIES,
                ),
            ],
                s.PLAIN_ELEMENT_PROPERTIES,
            ),
        ],
            s.PLAIN_ELEMENT_PROPERTIES,
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
                        s.MinorBlock([
                            s.LineElement(
                                s.StringLineObject(string_1),
                                s.PLAIN_ELEMENT_PROPERTIES,
                            ),
                        ],
                            s.PLAIN_ELEMENT_PROPERTIES,
                        ),
                    ],
                        s.PLAIN_ELEMENT_PROPERTIES,
                    ),
                    s.MajorBlock([
                        s.MinorBlock([
                            s.LineElement(
                                s.StringLineObject(string_2),
                                s.INDENTED_ELEMENT_PROPERTIES,
                            ),
                        ],
                            s.INDENTED_ELEMENT_PROPERTIES,
                        ),
                    ],
                        s.INDENTED_ELEMENT_PROPERTIES,
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
