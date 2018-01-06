import pathlib
import unittest
from typing import Dict, Sequence

from exactly_lib.section_document import document_parser as sut
from exactly_lib.section_document import model
from exactly_lib.section_document.document_parser import DocumentParser, new_parser_for, SectionConfiguration, \
    SectionsConfiguration
from exactly_lib.section_document.exceptions import SourceError, FileSourceError
from exactly_lib.section_document.model import InstructionInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_element_parser import ParsedSectionElement, ParsedInstruction, \
    new_empty_element, new_comment_element
from exactly_lib.util import line_source
from exactly_lib.util.line_source import Line
from exactly_lib_test.section_document.parse.test_resources.element_parser import \
    consume_current_line_and_return_it_as_line_sequence
from exactly_lib_test.section_document.test_resources.document_assertions import matches_document
from exactly_lib_test.section_document.test_resources.parse_source import source_of_lines
from exactly_lib_test.section_document.test_resources.section_contents_elements import InstructionInSection, \
    equals_instruction_without_description, \
    equals_multi_line_instruction_without_description, equals_empty_element, equals_comment_element
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import assert_equals_line, equals_line


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestSectionsConfiguration))
    ret_val.addTest(unittest.makeSuite(TestParseSingleLineElements))
    ret_val.addTest(unittest.makeSuite(TestParseMultiLineElements))
    ret_val.addTest(unittest.makeSuite(TestInvalidSyntax))
    return ret_val


_COMMENT_START = 'COMMENT'

_MULTI_LINE_INSTRUCTION_LINE_START = 'MULTI-LINE-INSTRUCTION'

EXPECTED_SOURCE_FILE_PATH = pathlib.Path('dummy source file path')
DUMMY_FILE_INCLUSION_RELATIVITY_ROOT = pathlib.Path.cwd()

NO_FILE_INCLUSIONS = []


class ParseTestBase(unittest.TestCase):
    def _parse_lines(self,
                     parser: DocumentParser,
                     lines: list) -> model.Document:
        ptc_source = source_of_lines(lines)
        return parser.parse(EXPECTED_SOURCE_FILE_PATH,
                            DUMMY_FILE_INCLUSION_RELATIVITY_ROOT,
                            ptc_source)

    def _parse_and_check(self,
                         parser: DocumentParser,
                         lines: list,
                         expected_document: Dict[str, Sequence[asrt.ValueAssertion[model.SectionContentElement]]]):
        # ACT #
        actual_document = self._parse_lines(parser, lines)
        # ASSERT #
        assertion = matches_document(expected_document)
        assertion.apply_without_message(self, actual_document)


class TestSectionsConfiguration(ParseTestBase):
    def test_WHEN_the_default_section_name_is_not_a_name_of_a_section_THEN_an_exception_SHOULD_be_raised(self):
        # ARRANGE #
        section_names = ['section 1', 'section 2']
        sections = [SectionConfiguration(name,
                                         SectionElementParserForEmptyCommentAndInstructionLines(
                                             name))
                    for name in section_names]
        default_section_name = 'not the name of a section'
        # ACT & ASSERT #
        with self.assertRaises(ValueError):
            SectionsConfiguration(
                tuple(sections),
                default_section_name=default_section_name)


class TestParseSingleLineElements(ParseTestBase):
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


class TestParseMultiLineElements(ParseTestBase):
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


class TestInvalidSyntax(ParseTestBase):
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
        assert_equals_line(self,
                           Line(1, 'instruction default'),
                           cm.exception.source_error.line)
        self.assertIsNone(cm.exception.maybe_section_name,
                          'Section name')

    def test_invalid_section_name_should_raise_exception(self):
        parser = parser_for_sections(['section-header'])
        cases = [
            NEA('first section header is invalid (missing closing bracket)',
                actual=['[section-header'],
                expected=assert_file_source_error(equals_line(Line(1, '[section-header')),
                                                  asrt.is_none)
                ),
            NEA('first section header is invalid (superfluous closing bracket)',
                actual=['[section-header]]'],
                expected=assert_file_source_error(equals_line(Line(1, '[section-header]]')),
                                                  asrt.is_none)
                ),
            NEA('first section header is invalid (content after closing bracket)',
                actual=['[section-header] superfluous'],
                expected=assert_file_source_error(equals_line(Line(1, '[section-header] superfluous')),
                                                  asrt.is_none)

                ),
            NEA('non-first section header is invalid',
                actual=['[section-header]',
                        'instruction 1',
                        '[section-header',
                        ]
                ,
                expected=assert_file_source_error(equals_line(Line(3, '[section-header')),
                                                  asrt.is_none)

                ),
            NEA('section header with unknown section name (as first section header)',
                actual=['[unknown-section-header]',
                        'instruction 1'
                        ]
                ,
                expected=assert_file_source_error(equals_line(Line(1, '[unknown-section-header]')),
                                                  asrt.is_none)
                ),
            NEA('section header with unknown section name (as non-first section header)',
                actual=['[section-header]',
                        'instruction 1',
                        '[unknown-section-header]',
                        'instruction 2',
                        ]
                ,
                expected=assert_file_source_error(equals_line(Line(3, '[unknown-section-header]')),
                                                  asrt.is_none)
                ),
        ]
        for nea in cases:
            with self.subTest(nea.name):
                with self.assertRaises(FileSourceError) as cm:
                    self._parse_lines(parser, nea.actual)
                nea.expected.apply_without_message(self, cm.exception)


def assert_file_source_error(line: asrt.ValueAssertion[Line] = asrt.anything_goes(),
                             maybe_section_name: asrt.ValueAssertion[str] = asrt.anything_goes()
                             ) -> asrt.ValueAssertion[FileSourceError]:
    return asrt.and_([
        asrt.sub_component('maybe_section_name',
                           FileSourceError.maybe_section_name.fget,
                           maybe_section_name),
        asrt.sub_component('line',
                           lambda fse: fse.source_error.line,
                           line),
    ])


def is_multi_line_instruction_line(line: str) -> bool:
    return line[:len(_MULTI_LINE_INSTRUCTION_LINE_START)] == _MULTI_LINE_INSTRUCTION_LINE_START


def is_comment_line(line: str) -> bool:
    return line[:len(_COMMENT_START)] == _COMMENT_START


class SectionElementParserForEmptyCommentAndInstructionLines(sut.SectionElementParser):
    def __init__(self, section_name: str):
        self._section_name = section_name

    def parse(self, source: ParseSource) -> ParsedSectionElement:
        current_line = source.current_line_text
        if current_line == '':
            return new_empty_element(consume_current_line_and_return_it_as_line_sequence(source))
        elif is_comment_line(current_line):
            return new_comment_element(consume_current_line_and_return_it_as_line_sequence(source))

        else:
            instruction_source = self._consume_instruction_source(source)
            return ParsedInstruction(instruction_source,
                                     InstructionInfo(InstructionInSection(self._section_name)))

    @staticmethod
    def _consume_instruction_source(source: ParseSource) -> line_source.LineSequence:
        current_line = source.current_line_text
        if is_multi_line_instruction_line(current_line):
            first_line_number = source.current_line_number
            lines = [current_line]
            source.consume_current_line()
            # Eat additional lines
            while source.has_current_line:
                current_line = source.current_line_text
                if is_multi_line_instruction_line(current_line):
                    lines.append(current_line)
                    source.consume_current_line()
                else:
                    break
            return line_source.LineSequence(first_line_number, tuple(lines))
        else:
            return consume_current_line_and_return_it_as_line_sequence(source)


class SectionElementParserThatFails(sut.SectionElementParser):
    def parse(self, source: ParseSource) -> ParsedSectionElement:
        raise SourceError(consume_current_line_and_return_it_as_line_sequence(source).first_line,
                          'Unconditional failure')


def parser_for_section2_that_fails_unconditionally() -> DocumentParser:
    return parser_with_successful_and_failing_section_parsers('section 1', 'section 2')


def parser_with_successful_and_failing_section_parsers(successful_section: str,
                                                       failing_section: str,
                                                       default_section: str = None) -> DocumentParser:
    configuration = SectionsConfiguration(
        (SectionConfiguration(successful_section,
                              SectionElementParserForEmptyCommentAndInstructionLines(
                                  successful_section)),
         SectionConfiguration(failing_section,
                              SectionElementParserThatFails())),
        default_section_name=default_section)

    return new_parser_for(configuration)


def parser_for_sections(section_names: list,
                        default_section_name: str = None) -> DocumentParser:
    sections = [SectionConfiguration(name,
                                     SectionElementParserForEmptyCommentAndInstructionLines(name))
                for name in section_names]
    if default_section_name is not None:
        if default_section_name not in section_names:
            raise ValueError('Test setup: The given default section %s is not the name of a section (%s)' % (
                default_section_name,
                section_names,
            ))
    configuration = SectionsConfiguration(
        tuple(sections),
        default_section_name=default_section_name)
    return new_parser_for(configuration)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
