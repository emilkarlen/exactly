import pathlib
import unittest

from exactly_lib.processing.parse import file_inclusion_directive_parser as sut
from exactly_lib.section_document.section_element_parsing import SectionElementError, \
    RecognizedSectionElementSourceError
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import source_of_lines
from exactly_lib_test.section_document.test_resources.parse_source_assertions import is_at_beginning_of_line
from exactly_lib_test.section_document.test_resources.parsed_element_assertions import is_file_inclusion_directive, \
    matches_file_inclusion_directive
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.line_source_assertions import matches_line_sequence


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParse)


class TestParse(unittest.TestCase):
    def test_WHEN_source_does_not_start_with_directive_name_THEN_return_value_SHOULD_be_none(self):
        # ARRANGE #
        inclusion_directive_name = 'the-directive'
        parser = sut.FileInclusionDirectiveParser(inclusion_directive_name)
        source = source_of_lines([
            inclusion_directive_name + 'non-space arg',
            'second line',
        ])
        # ACT #
        actual = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
        # ASSERT #
        self.assertIsNone(actual, 'return value')

        expected_source = is_at_beginning_of_line(1)
        expected_source.apply_with_message(self, source, 'source')

    def test_WHEN_source_does_start_with_directive_name_but_invalid_number_of_arguments_follows_THEN_exception_SHOULD_be_raised(
            self):
        # ARRANGE #
        inclusion_directive_name = 'include'
        parser = sut.FileInclusionDirectiveParser(inclusion_directive_name)
        cases = [
            NameAndValue('missing argument',
                         inclusion_directive_name,
                         ),
            NameAndValue('superfluous arguments',
                         inclusion_directive_name + '   arg1 superfluous',
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                source = source_of_lines([
                    case.value,
                    'second line',
                ])
                # ACT #
                with self.assertRaises(RecognizedSectionElementSourceError) as cm:
                    # ACT & ASSERT #
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                actual_exception = cm.exception
                assert isinstance(actual_exception, SectionElementError)

                expected_invalid_source = matches_line_sequence(
                    first_line_number=asrt.equals(1),
                    lines=asrt.matches_sequence([
                        asrt.equals(case.value)
                    ]))

                expected_invalid_source.apply_with_message(self, actual_exception.source, 'source')

    def test_valid_syntax_of_inclusion_directive(self):
        # ARRANGE #
        inclusion_directive_name = 'incl-directive'
        parser = sut.FileInclusionDirectiveParser(inclusion_directive_name)

        file_name = 'the-file-name'
        cases = [
            NameAndValue('simple inclusion',
                         inclusion_directive_name + ' ' + file_name,
                         ),
            NameAndValue('some superfluous space around path argument',
                         inclusion_directive_name + '   ' + file_name + '     ',
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                source = source_of_lines([
                    case.value,
                    'second line',
                ])
                # ACT #
                actual = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                # ASSERT #
                expected_directive = is_file_inclusion_directive(
                    matches_file_inclusion_directive(
                        files_to_include=asrt.matches_sequence([
                            asrt.equals(pathlib.Path(file_name)),
                        ]),
                        source=matches_line_sequence(
                            first_line_number=asrt.equals(1),
                            lines=asrt.matches_sequence([
                                asrt.equals(case.value)
                            ]))
                    ))
                expected_directive.apply_with_message(self,
                                                      actual,
                                                      'parsed directive')

                expected_source = is_at_beginning_of_line(2)
                expected_source.apply_with_message(self, source, 'source')

    def test_path_argument_SHOULD_use_posix_syntax(self):
        # ARRANGE #
        inclusion_directive_name = 'incl-directive'
        parser = sut.FileInclusionDirectiveParser(inclusion_directive_name)

        path_arg = pathlib.PurePosixPath('first') / 'second'
        inclusion_directive_line = inclusion_directive_name + ' ' + str(path_arg)
        source = source_of_lines([
            inclusion_directive_line,
            'second line',
        ])
        # ACT #
        actual = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
        # ASSERT #
        expected_directive = is_file_inclusion_directive(
            matches_file_inclusion_directive(
                files_to_include=asrt.matches_sequence([
                    asrt.equals(pathlib.Path(path_arg)),
                ]),
                source=matches_line_sequence(
                    first_line_number=asrt.equals(1),
                    lines=asrt.matches_sequence([
                        asrt.equals(inclusion_directive_line)
                    ]))
            ))
        expected_directive.apply_with_message(self,
                                              actual,
                                              'parsed directive')

        expected_source = is_at_beginning_of_line(2)
        expected_source.apply_with_message(self, source, 'source')
