import unittest

from exactly_lib_test.section_document.document_parser.test_resources.misc import parser_for_sections, \
    parser_for_section2_that_fails_unconditionally
from exactly_lib_test.section_document.document_parser.test_resources.parse_test_case_base import ParseTestBase, \
    EXPECTED_SOURCE_FILE_PATH
from exactly_lib_test.section_document.test_resources.element_assertions import equals_comment_element, \
    equals_empty_element, equals_instruction_without_description, equals_multi_line_instruction_without_description

NO_FILE_INCLUSIONS = []


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSectionHandling)


class TestSectionHandling(ParseTestBase):
    def test_sections_without_elements_are_registered(self):
        # ARRANGE #
        parser = parser_for_sections(['section 1', 'section 2'])
        source_lines = ['[section 1]',
                        '[section 2]',
                        ]
        expected = {
            'section 1': [],
            'section 2': [],
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)

    def test_initial_empty_lines_and_comment_lines_should_be_ignored_when_there_is_no_default_section(self):
        # ARRANGE #
        parser = parser_for_sections(['section 1', 'section 2'])
        source_lines = ['# standard-comment default',
                        '',
                        '[section 1]',
                        'COMMENT 1',
                        '',
                        'instruction 1',
                        ]
        expected = {
            'section 1': [
                equals_comment_element(4, 'COMMENT 1'),
                equals_empty_element(5, ''),
                equals_instruction_without_description(6, 'instruction 1', 'section 1', EXPECTED_SOURCE_FILE_PATH,
                                                       NO_FILE_INCLUSIONS),
            ],
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)

    def test_valid_default_and_named_section(self):
        # ARRANGE #
        parser = parser_for_sections(['section 1', 'default'],
                                     default_section_name='default')
        source_lines = ['COMMENT default',
                        '',
                        'instruction default',
                        '[section 1]',
                        'COMMENT 1',
                        'instruction 1']
        default_section_contents = (
            equals_comment_element(1, 'COMMENT default'),
            equals_empty_element(2, ''),
            equals_instruction_without_description(3, 'instruction default', 'default', EXPECTED_SOURCE_FILE_PATH,
                                                   NO_FILE_INCLUSIONS)
        )
        section1_contents = (
            equals_comment_element(5, 'COMMENT 1'),
            equals_instruction_without_description(6, 'instruction 1', 'section 1', EXPECTED_SOURCE_FILE_PATH,
                                                   NO_FILE_INCLUSIONS)
        )
        expected = {
            'default': default_section_contents,
            'section 1': section1_contents,
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)

    def test_valid_default_and_named_section__without_default_section_contents(self):
        # ARRANGE #
        parser = parser_for_sections(['section 1', 'default'],
                                     default_section_name='default')
        source_lines = ['[section 1]',
                        'COMMENT 1',
                        'instruction 1']
        section1_contents = (
            equals_comment_element(2, 'COMMENT 1'),
            equals_instruction_without_description(3, 'instruction 1', 'section 1', EXPECTED_SOURCE_FILE_PATH,
                                                   NO_FILE_INCLUSIONS)
        )
        expected = {
            'section 1': section1_contents,
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)

    def test_valid_section_with_comment_and_instruction(self):
        # ARRANGE #
        parser = parser_for_sections(['section 1', 'section 2'])
        source_lines = ['[section 1]',
                        'COMMENT',
                        'instruction'
                        ]
        expected = {
            'section 1': [
                equals_comment_element(2, 'COMMENT'),
                equals_instruction_without_description(3, 'instruction', 'section 1', EXPECTED_SOURCE_FILE_PATH,
                                                       NO_FILE_INCLUSIONS)
            ]
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)

    def test_valid_section_with_fragmented_sections(self):
        # ARRANGE #
        source_lines = ['[section 1]',
                        'COMMENT 1',
                        '',
                        '[section 2]',
                        'instruction 2',
                        '[section 1]',
                        'instruction 1'
                        ]
        parser = parser_for_sections(['section 1', 'section 2'])
        expected = {
            'section 1': [
                equals_comment_element(2, 'COMMENT 1'),
                equals_empty_element(3, ''),
                equals_instruction_without_description(7, 'instruction 1', 'section 1', EXPECTED_SOURCE_FILE_PATH,
                                                       NO_FILE_INCLUSIONS)
            ],
            'section 2': [
                equals_instruction_without_description(5, 'instruction 2', 'section 2', EXPECTED_SOURCE_FILE_PATH,
                                                       NO_FILE_INCLUSIONS),

            ]
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)

    def test_the_instruction_parser_for_the_current_section_should_be_used(self):
        # ARRANGE #
        parser = parser_for_section2_that_fails_unconditionally()
        source_lines = ['[section 1]',
                        'instruction 1',
                        ]
        expected = {
            'section 1': [
                equals_instruction_without_description(2, 'instruction 1', 'section 1', EXPECTED_SOURCE_FILE_PATH,
                                                       NO_FILE_INCLUSIONS),
            ]
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)

    def test_adjacent_section_lines(self):
        # ARRANGE #
        parser = parser_for_sections(['section 1', 'section 2'])
        source_lines = ['[section 1]',
                        'instruction 1',
                        '[section 1]',
                        '[section 2]',
                        '[section 1]',
                        'MULTI-LINE-INSTRUCTION 2-1',
                        'MULTI-LINE-INSTRUCTION 2-2',
                        'MULTI-LINE-INSTRUCTION 2-3',
                        ]
        expected = {
            'section 1': [
                equals_instruction_without_description(2, 'instruction 1',
                                                       'section 1',
                                                       EXPECTED_SOURCE_FILE_PATH,
                                                       NO_FILE_INCLUSIONS),
                equals_multi_line_instruction_without_description(6,
                                                                  ['MULTI-LINE-INSTRUCTION 2-1',
                                                                   'MULTI-LINE-INSTRUCTION 2-2',
                                                                   'MULTI-LINE-INSTRUCTION 2-3'],
                                                                  'section 1',
                                                                  EXPECTED_SOURCE_FILE_PATH,
                                                                  NO_FILE_INCLUSIONS),
            ],
            'section 2': [],
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
