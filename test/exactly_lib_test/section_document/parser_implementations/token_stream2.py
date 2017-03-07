import unittest

from exactly_lib.section_document.parser_implementations import token_stream2 as sut
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenSyntaxError
from exactly_lib_test.section_document.parser_implementations.test_resources import assert_quoted, assert_plain


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
                ts = sut.TokenStream2(first_line)
                self.assertTrue(ts.is_null)

    def test_invalid_token(self):
        test_cases = [
            '\'missing end single quote',
        ]
        for first_line in test_cases:
            with self.subTest(msg=repr(first_line)):
                with self.assertRaises(TokenSyntaxError):
                    sut.TokenStream2(first_line)

    def test_valid_token(self):
        test_cases = [
            ('token',
             assert_plain('token'),
             '',
             ),
            ('<<->> other_token',
             assert_plain('<<->>'),
             'other_token'
             ),
        ]
        for first_line, token_assertion, expected_remaining_source in test_cases:
            with self.subTest(msg=repr(first_line)):
                ts = sut.TokenStream2(first_line)
                token_assertion.apply_with_message(self, ts.head, 'token')
                actual_remaining_source = first_line[ts.position:]
                self.assertEqual(expected_remaining_source,
                                 actual_remaining_source,
                                 'remaining source')


class TestParseTokenOnCurrentLine(unittest.TestCase):
    def test_invalid_quoting(self):
        test_cases = [
            '\'missing end single quote',
            'missing_start_single_quote\'',
            '\"missing end double quote',
            'missing_start_double_quote\"',
        ]
        for first_line in test_cases:
            with self.subTest(msg=repr(first_line)):
                with self.assertRaises(TokenSyntaxError):
                    sut.TokenStream2(first_line)

    def test_valid_token(self):
        test_cases = [
            ('token',
             assert_plain('token'),
             '',
             ),
            ('    token_preceded_by_space',
             assert_plain('token_preceded_by_space'),
             '',
             ),
            ('token_followed_by_space ',
             assert_plain('token_followed_by_space'),
             '',
             ),
            ('token_followed_by_2_space  ',
             assert_plain('token_followed_by_2_space'),
             ' ',
             ),
            ('token_followed_by_other_token other_token',
             assert_plain('token_followed_by_other_token'),
             'other_token',
             ),
            ('token_followed_by_other_token_with_2_space_between  other_token',
             assert_plain('token_followed_by_other_token_with_2_space_between'),
             ' other_token',
             ),
            ('<<->> other_token',
             assert_plain('<<->>'),
             'other_token',
             ),
            ('\'single quoted\'',
             assert_quoted('single quoted', '\'single quoted\''),
             '',
             ),
            ('\"double quoted\"',
             assert_quoted('double quoted', '\"double quoted\"'),
             '',
             ),
            (' \'quoted preceded by space\'',
             assert_quoted('quoted preceded by space', '\'quoted preceded by space\''),
             '',
             ),
            (' \'quoted followed by space\' ',
             assert_quoted('quoted followed by space', '\'quoted followed by space\''),
             '',
             ),
            (' \'quoted token followed by other token\' \'other_token\'',
             assert_quoted('quoted token followed by other token',
                           '\'quoted token followed by other token\''),
             '\'other_token\'',
             ),
        ]
        for first_line, token_assertion, expected_remaining_source in test_cases:
            with self.subTest(msg=repr(first_line)):
                ts = sut.TokenStream2(first_line)
                token_assertion.apply_with_message(self, ts.head, 'token')
                actual_remaining_source = first_line[ts.position:]
                self.assertEqual(expected_remaining_source,
                                 actual_remaining_source,
                                 'remaining source')
