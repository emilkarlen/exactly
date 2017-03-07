import unittest

from exactly_lib.section_document.parser_implementations import token_parse as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.section_document.parser_implementations.test_resources import assert_quoted, assert_plain
from exactly_lib_test.section_document.test_resources.parse_source import source_is_not_at_end, assert_source
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseTokenOnCurrentLine),
        unittest.makeSuite(TestParseTokenOrNoneOnCurrentLine),
    ])


class TestParseTokenOrNoneOnCurrentLine(unittest.TestCase):
    def test_no_token_on_remaining_part_of_current_line(self):
        test_cases = [
            '',
            '     ',
        ]
        for first_line in test_cases:
            with self.subTest(msg=repr(first_line)):
                source = remaining_source(first_line)
                actual = sut.parse_token_or_none_on_current_line(source)
                self.assertIsNone(actual)
                assert_source(is_at_eol=asrt.is_true)

    def test_invalid_token(self):
        test_cases = [
            '\'missing end single quote',
        ]
        for first_line in test_cases:
            with self.subTest(msg=repr(first_line)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    source = remaining_source(first_line)
                    sut.parse_token_or_none_on_current_line(source)

    def test_valid_token(self):
        test_cases = [
            ('token',
             assert_plain('token'),
             assert_source(is_at_eol=asrt.is_true,
                           has_current_line=asrt.is_true,
                           current_line_number=asrt.equals(1))),
            ('<<->> other_token',
             assert_plain('<<->>'),
             source_is_not_at_end(remaining_part_of_current_line=asrt.equals(' other_token'),
                                  current_line_number=asrt.equals(1))),
        ]
        for first_line, token_assertion, source_assertion in test_cases:
            with self.subTest(msg=repr(first_line)):
                source = remaining_source(first_line)
                actual = sut.parse_token_or_none_on_current_line(source)
                token_assertion.apply_with_message(self, actual, 'token')
                source_assertion.apply_with_message(self, source, 'source')


class TestParseTokenOnCurrentLine(unittest.TestCase):
    def test_no_token_on_remaining_part_of_current_line(self):
        test_cases = [
            '',
            '     ',
        ]
        for first_line in test_cases:
            with self.subTest(msg=repr(first_line)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    source = remaining_source(first_line)
                    sut.parse_token_on_current_line(source)

    def test_invalid_quoting(self):
        test_cases = [
            '\'missing end single quote',
            'missing_start_single_quote\'',
            '\"missing end double quote',
            'missing_start_double_quote\"',
        ]
        for first_line in test_cases:
            with self.subTest(msg=repr(first_line)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    source = remaining_source(first_line)
                    sut.parse_token_on_current_line(source)

    def test_valid_token(self):
        test_cases = [
            ('token',
             assert_plain('token'),
             assert_source(is_at_eol=asrt.is_true,
                           has_current_line=asrt.is_true,
                           current_line_number=asrt.equals(1))),
            ('    token_preceded_by_space',
             assert_plain('token_preceded_by_space'),
             assert_source(is_at_eol=asrt.is_true,
                           has_current_line=asrt.is_true,
                           current_line_number=asrt.equals(1))),
            ('token_followed_by_space ',
             assert_plain('token_followed_by_space'),
             source_is_not_at_end(remaining_part_of_current_line=asrt.equals(' '),
                                  current_line_number=asrt.equals(1))),
            ('token_followed_by_other_token other_token',
             assert_plain('token_followed_by_other_token'),
             source_is_not_at_end(remaining_part_of_current_line=asrt.equals(' other_token'),
                                  current_line_number=asrt.equals(1))),
            ('<<->> other_token',
             assert_plain('<<->>'),
             source_is_not_at_end(remaining_part_of_current_line=asrt.equals(' other_token'),
                                  current_line_number=asrt.equals(1))),
            ('\'single quoted\'',
             assert_quoted('single quoted', '\'single quoted\''),
             assert_source(is_at_eol=asrt.is_true,
                           has_current_line=asrt.is_true,
                           current_line_number=asrt.equals(1))),
            ('\"double quoted\"',
             assert_quoted('double quoted', '\"double quoted\"'),
             assert_source(is_at_eol=asrt.is_true,
                           has_current_line=asrt.is_true,
                           current_line_number=asrt.equals(1))),
            (' \'quoted preceded by space\'',
             assert_quoted('quoted preceded by space', '\'quoted preceded by space\''),
             assert_source(is_at_eol=asrt.is_true,
                           has_current_line=asrt.is_true,
                           current_line_number=asrt.equals(1))),
            (' \'quoted followed by space\' ',
             assert_quoted('quoted followed by space', '\'quoted followed by space\''),
             source_is_not_at_end(remaining_part_of_current_line=asrt.equals(' '),
                                  current_line_number=asrt.equals(1))),
            (' \'quoted token followed by other token\' \'other_token\'',
             assert_quoted('quoted token followed by other token',
                           '\'quoted token followed by other token\''),
             source_is_not_at_end(remaining_part_of_current_line=asrt.equals(' \'other_token\''),
                                  current_line_number=asrt.equals(1))),
        ]
        for first_line, token_assertion, source_assertion in test_cases:
            with self.subTest(msg=repr(first_line)):
                source = remaining_source(first_line)
                actual = sut.parse_token_on_current_line(source)
                token_assertion.apply_with_message(self, actual, 'token')
                source_assertion.apply_with_message(self, source, 'source')
