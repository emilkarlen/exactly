import unittest

from exactly_lib.section_document.document_parsers import new_parser_for
from exactly_lib.section_document.exceptions import FileSourceError
from exactly_lib.section_document.section_parsing import SectionConfiguration, SectionsConfiguration
from exactly_lib.section_document.source_location import SourceLocation
from exactly_lib.section_document.syntax import section_header
from exactly_lib.util import line_source
from exactly_lib.util.line_source import Line, single_line_sequence
from exactly_lib_test.section_document.document_parser.section_handling import NO_FILE_INCLUSIONS
from exactly_lib_test.section_document.document_parser.test_resources.exception_assertions import \
    matches_file_source_error, file_source_error_equals_line
from exactly_lib_test.section_document.document_parser.test_resources.misc import \
    parser_for_section2_that_fails_unconditionally, \
    parser_for_sections
from exactly_lib_test.section_document.document_parser.test_resources.parse_test_case_base import \
    EXPECTED_SOURCE_FILE_PATH, ParseTestBase
from exactly_lib_test.section_document.test_resources.element_assertions import equals_instruction_without_description, \
    equals_multi_line_instruction_without_description, equals_empty_element
from exactly_lib_test.section_document.test_resources.element_parsers import SectionElementParserThatReturnsNone
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import assert_equals_line_sequence


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSourceHandling),
        unittest.makeSuite(TestInvalidSyntax),
    ])


class TestSourceHandling(ParseTestBase):
    def test_single_multi_line_instruction_that_is_actually_only_a_single_line_in_default_section(self):
        # ARRANGE #
        parser = parser_for_sections(['default'],
                                     default_section_name='default')
        source_lines = ['MULTI-LINE-INSTRUCTION 1'
                        ]
        expected = {
            'default': [
                equals_instruction_without_description(1, 'MULTI-LINE-INSTRUCTION 1', 'default',
                                                       EXPECTED_SOURCE_FILE_PATH,
                                                       NO_FILE_INCLUSIONS),
            ],
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)

    def test_single_multi_line_instruction_in_default_section_that_occupies_whole_doc(self):
        # ARRANGE #
        parser = parser_for_sections(['section 1', 'default'],
                                     default_section_name='default')
        source_lines = ['MULTI-LINE-INSTRUCTION 1',
                        'MULTI-LINE-INSTRUCTION 2']
        expected = {
            'default': [
                equals_multi_line_instruction_without_description(1,
                                                                  ['MULTI-LINE-INSTRUCTION 1',
                                                                   'MULTI-LINE-INSTRUCTION 2'],
                                                                  'default',
                                                                  EXPECTED_SOURCE_FILE_PATH,
                                                                  NO_FILE_INCLUSIONS),
            ],
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)

    def test_single_multi_line_instruction_in_default_section_surrounded_by_empty_lines(self):
        # ARRANGE #
        parser = parser_for_sections(['section 1', 'default'],
                                     default_section_name='default')
        source_lines = ['',
                        'MULTI-LINE-INSTRUCTION 1',
                        'MULTI-LINE-INSTRUCTION 2',
                        ''
                        ]
        expected = {
            'default': [
                equals_empty_element(1, ''),
                equals_multi_line_instruction_without_description(2,
                                                                  ['MULTI-LINE-INSTRUCTION 1',
                                                                   'MULTI-LINE-INSTRUCTION 2'],
                                                                  'default',
                                                                  EXPECTED_SOURCE_FILE_PATH,
                                                                  NO_FILE_INCLUSIONS),
            ],
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)

    def test_single_multi_line_instruction_in_default_section_ended_by_section_header(self):
        # ARRANGE #
        parser = parser_for_sections(['section 1', 'default'],
                                     default_section_name='default')
        source_lines = ['',
                        'MULTI-LINE-INSTRUCTION 1',
                        'MULTI-LINE-INSTRUCTION 2',
                        '[section 1]',
                        'instruction 1',
                        ]
        expected = {
            'default': [
                equals_empty_element(1, ''),
                equals_multi_line_instruction_without_description(2,
                                                                  ['MULTI-LINE-INSTRUCTION 1',
                                                                   'MULTI-LINE-INSTRUCTION 2'],
                                                                  'default',
                                                                  EXPECTED_SOURCE_FILE_PATH,
                                                                  NO_FILE_INCLUSIONS),

            ],
            'section 1': [
                equals_instruction_without_description(5, 'instruction 1',
                                                       'section 1',
                                                       EXPECTED_SOURCE_FILE_PATH,
                                                       NO_FILE_INCLUSIONS),
            ],
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)

    def test_mix_of_instructions_without_default_section(self):
        # ARRANGE #
        parser = parser_for_sections(['section 1'])
        source_lines = ['',
                        '[section 1]',
                        'instruction 1',
                        'MULTI-LINE-INSTRUCTION 2-1',
                        'MULTI-LINE-INSTRUCTION 2-2',
                        'MULTI-LINE-INSTRUCTION 2-3',
                        'instruction 3']
        expected = {
            'section 1': [
                equals_instruction_without_description(3, 'instruction 1', 'section 1', EXPECTED_SOURCE_FILE_PATH,
                                                       NO_FILE_INCLUSIONS),
                equals_multi_line_instruction_without_description(4,
                                                                  ['MULTI-LINE-INSTRUCTION 2-1',
                                                                   'MULTI-LINE-INSTRUCTION 2-2',
                                                                   'MULTI-LINE-INSTRUCTION 2-3'],
                                                                  'section 1',
                                                                  EXPECTED_SOURCE_FILE_PATH,
                                                                  NO_FILE_INCLUSIONS),
                equals_instruction_without_description(7, 'instruction 3', 'section 1', EXPECTED_SOURCE_FILE_PATH,
                                                       NO_FILE_INCLUSIONS),
            ],
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)

    def test_multi_line_instruction_at_end_of_file_inside_section(self):
        # ARRANGE #
        parser = parser_for_sections(['section 1', 'section 2'])
        source_lines = ['',
                        '[section 1]',
                        'instruction 1',
                        'MULTI-LINE-INSTRUCTION 2-1',
                        'MULTI-LINE-INSTRUCTION 2-2',
                        'MULTI-LINE-INSTRUCTION 2-3',
                        ]
        expected = {
            'section 1': [
                equals_instruction_without_description(3, 'instruction 1',
                                                       'section 1',
                                                       EXPECTED_SOURCE_FILE_PATH,
                                                       NO_FILE_INCLUSIONS),
                equals_multi_line_instruction_without_description(4,
                                                                  ['MULTI-LINE-INSTRUCTION 2-1',
                                                                   'MULTI-LINE-INSTRUCTION 2-2',
                                                                   'MULTI-LINE-INSTRUCTION 2-3'],
                                                                  'section 1',
                                                                  EXPECTED_SOURCE_FILE_PATH,
                                                                  NO_FILE_INCLUSIONS),
            ],
        }
        # ACT & ASSERT #
        self._parse_and_check(parser, source_lines, expected)


class TestInvalidSyntax(ParseTestBase):
    def test_element_parser_SHOULD_be_able_to_report_syntax_error_by_returning_None(self):
        # ARRANGE #
        section_name = 'section-name'
        parser = new_parser_for(
            SectionsConfiguration([SectionConfiguration(section_name,
                                                        SectionElementParserThatReturnsNone())],
                                  default_section_name=section_name))
        unrecognized_line = 'unrecognized'
        cases = [
            NEA('unrecognized source inside declared section',
                actual=[section_header(section_name),
                        unrecognized_line,
                        'following line'],
                expected=matches_file_source_error(
                    maybe_section_name=asrt.equals(section_name),
                    location_path=[
                        SourceLocation(single_line_sequence(2, unrecognized_line),
                                       EXPECTED_SOURCE_FILE_PATH)
                    ])
                ),
            NEA('unrecognized source in default section',
                actual=[unrecognized_line,
                        'following line'],
                expected=matches_file_source_error(
                    maybe_section_name=asrt.equals(section_name),
                    location_path=[
                        SourceLocation(single_line_sequence(1, unrecognized_line),
                                       EXPECTED_SOURCE_FILE_PATH)
                    ],
                )),
        ]
        for nea in cases:
            with self.subTest(nea.name):
                with self.assertRaises(FileSourceError) as cm:
                    # ACT & ASSERT #
                    self._parse_lines(parser, nea.actual)
                nea.expected.apply_without_message(self, cm.exception)

    def test_instruction_in_default_section_SHOULD_not_be_allowed_when_there_is_no_default_section(self):
        # ARRANGE #
        parser = parser_for_sections(['section 1'])
        source_lines = ['instruction default',
                        '[section 1]',
                        'instruction 1']
        # ACT & ASSERT #
        with self.assertRaises(FileSourceError) as cm:
            self._parse_lines(parser,
                              source_lines)
        # ASSERT #
        assert_equals_line_sequence(self,
                                    line_source.single_line_sequence(1, 'instruction default'),
                                    cm.exception.source)
        self.assertIsNone(cm.exception.maybe_section_name,
                          'Section name')

    def test_invalid_section_name_should_raise_exception(self):
        parser = parser_for_sections(['section-header'])
        cases = [
            NEA('first section header is invalid (missing closing bracket)',
                actual=['[section-header'],
                expected=file_source_error_equals_line(Line(1, '[section-header'),
                                                       asrt.is_none)
                ),
            NEA('first section header is invalid (superfluous closing bracket)',
                actual=['[section-header]]'],
                expected=file_source_error_equals_line(Line(1, '[section-header]]'),
                                                       asrt.is_none)
                ),
            NEA('first section header is invalid (content after closing bracket)',
                actual=['[section-header] superfluous'],
                expected=file_source_error_equals_line(Line(1, '[section-header] superfluous'),
                                                       asrt.is_none)

                ),
            NEA('non-first section header is invalid',
                actual=['[section-header]',
                        'instruction 1',
                        '[section-header',
                        ]
                ,
                expected=file_source_error_equals_line(Line(3, '[section-header'),
                                                       asrt.is_none)

                ),
            NEA('section header with unknown section name (as first section header)',
                actual=['[unknown-section-header]',
                        'instruction 1'
                        ]
                ,
                expected=file_source_error_equals_line(Line(1, '[unknown-section-header]'),
                                                       asrt.is_none)
                ),
            NEA('section header with unknown section name (as non-first section header)',
                actual=['[section-header]',
                        'instruction 1',
                        '[unknown-section-header]',
                        'instruction 2',
                        ]
                ,
                expected=file_source_error_equals_line(Line(3, '[unknown-section-header]'),
                                                       asrt.is_none)
                ),
        ]
        for nea in cases:
            with self.subTest(nea.name):
                with self.assertRaises(FileSourceError) as cm:
                    self._parse_lines(parser, nea.actual)
                nea.expected.apply_without_message(self, cm.exception)

    def test_parse_should_fail_when_instruction_parser_fails(self):
        # ARRANGE #
        parser = parser_for_section2_that_fails_unconditionally()
        source_lines = ['[section 2]',
                        'instruction 2',
                        ]
        # ACT & ASSERT #
        with self.assertRaises(FileSourceError) as cm:
            self._parse_lines(
                parser,
                source_lines)
        # ASSERT #
        self.assertEqual('section 2',
                         cm.exception.maybe_section_name)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
