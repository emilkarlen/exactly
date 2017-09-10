import unittest

from exactly_lib.section_document.parser_implementations import token_stream as sut
from exactly_lib.section_document.parser_implementations.token_stream import TokenSyntaxError, LookAheadState
from exactly_lib_test.section_document.parser_implementations.test_resources.token_stream_assertions import \
    assert_quoted, assert_plain, assert_token_stream
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseTokenOnCurrentLine),
        unittest.makeSuite(TestParseTokenOrNoneOnCurrentLine),
        unittest.makeSuite(TestConsume),
        unittest.makeSuite(TestConsumeRemainingPartOfCurrentLineAsPlainString),
        unittest.makeSuite(TestMisc),
    ])


def assert_is_null(put: unittest.TestCase, actual: sut.TokenStream):
    put.assertTrue(actual.is_null,
                   'is null')
    put.assertIs(LookAheadState.NULL,
                 actual.look_ahead_state,
                 'look ahead state')


def assert_is_not_null(put: unittest.TestCase, actual: sut.TokenStream):
    put.assertFalse(actual.is_null,
                    'is null')
    put.assertIsNot(LookAheadState.NULL,
                    actual.look_ahead_state,
                    'look ahead state')


class TestParseTokenOrNoneOnCurrentLine(unittest.TestCase):
    def test_no_token_on_remaining_part_of_current_line(self):
        test_cases = [
            '',
            '     ',
        ]
        for first_line in test_cases:
            with self.subTest(msg=repr(first_line)):
                ts = sut.TokenStream(first_line)
                assert_is_null(self, ts)

    def test_invalid_token(self):
        test_cases = [
            '\'missing end single quote',
        ]
        for first_line in test_cases:
            with self.subTest(msg=repr(first_line)):
                with self.assertRaises(TokenSyntaxError):
                    sut.TokenStream(first_line)

    def test_valid_token(self):
        test_cases = [
            ('token',
             assert_plain('token'),
             ),
            ('<<->> other_token',
             assert_plain('<<->>'),
             ),
        ]
        for first_line, token_assertion in test_cases:
            with self.subTest(msg=repr(first_line)):
                ts = sut.TokenStream(first_line)
                token_assertion.apply_with_message(self, ts.head, 'token')
                actual_remaining_source = first_line[ts.position:]
                self.assertEqual(first_line,
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
                    sut.TokenStream(first_line)

    def test_valid_token(self):
        test_cases = [
            ('token',
             assert_plain('token'),
             ),
            ('    token_preceded_by_space',
             assert_plain('token_preceded_by_space'),
             ),
            ('token_followed_by_space ',
             assert_plain('token_followed_by_space'),
             ),
            ('token_followed_by_2_space  ',
             assert_plain('token_followed_by_2_space'),
             ),
            ('token_followed_by_other_token other_token',
             assert_plain('token_followed_by_other_token'),
             ),
            ('token_followed_by_other_token_with_2_space_between  other_token',
             assert_plain('token_followed_by_other_token_with_2_space_between'),
             ),
            ('<<->> other_token',
             assert_plain('<<->>'),
             ),
            ('\'single quoted\'',
             assert_quoted('single quoted', '\'single quoted\''),
             ),
            ('\"double quoted\"',
             assert_quoted('double quoted', '\"double quoted\"'),
             ),
            (' \'quoted preceded by space\'',
             assert_quoted('quoted preceded by space', '\'quoted preceded by space\''),
             ),
            (' \'quoted followed by space\' ',
             assert_quoted('quoted followed by space', '\'quoted followed by space\''),
             ),
            (' \'quoted token followed by other token\' \'other_token\'',
             assert_quoted('quoted token followed by other token',
                           '\'quoted token followed by other token\''),
             ),
        ]
        for first_line, token_assertion in test_cases:
            with self.subTest(msg=repr(first_line)):
                ts = sut.TokenStream(first_line)
                token_assertion.apply_with_message(self, ts.head, 'token')
                self.assertEqual(first_line,
                                 ts.remaining_source,
                                 'remaining source')
                assert_is_not_null(self, ts)


class TestConsume(unittest.TestCase):
    def test_single_token(self):
        test_cases = [
            ('a', assert_plain('a'), ''),
            ('b ', assert_plain('b'), ''),
            ('c  ', assert_plain('c'), ' '),
            ('x \n', assert_plain('x'), '\n'),
            ('x\n', assert_plain('x'), '\n'),
        ]
        for source, expected_token, remaining_source in test_cases:
            with self.subTest(msg=repr(source)):
                ts = sut.TokenStream(source)
                # ACT #
                consumed_token = ts.consume()
                # ASSERT #
                expected_token.apply_with_message(self, consumed_token, 'token')
                assert_is_null(self, ts)
                self.assertEqual(remaining_source, ts.remaining_source,
                                 'remaining_source')

    def test_multiple_tokens(self):
        test_cases = [
            ('a A', 'A', 'A'),
            ('b  B', 'B', ' B'),
            ('c  C ', 'C', ' C '),
            ('d  D  ', 'D', ' D  '),
            ('a A\n_', 'A', 'A\n_'),
        ]
        for source, second_token, remaining_source in test_cases:
            with self.subTest(msg=repr(source)):
                ts = sut.TokenStream(source)
                ts.consume()
                assert_is_not_null(self, ts)
                self.assertEqual(second_token, ts.head.string,
                                 'second token')
                self.assertEqual(remaining_source, ts.remaining_source,
                                 'remaining_source')


class TestConsumeRemainingPartOfCurrentLineAsPlainString(unittest.TestCase):
    def test(self):
        test_cases = [
            # Single token
            ('a', 'a',
             assert_token_stream(is_null=asrt.is_true,
                                 look_ahead_state=asrt.is_(LookAheadState.NULL),
                                 position=asrt.equals(1),
                                 remaining_source=asrt.equals(''))),
            ('b ', 'b ',
             assert_token_stream(is_null=asrt.is_true,
                                 look_ahead_state=asrt.is_(LookAheadState.NULL),
                                 position=asrt.equals(2),
                                 remaining_source=asrt.equals(''))),
            ('x \n', 'x ',
             assert_token_stream(is_null=asrt.is_true,
                                 look_ahead_state=asrt.is_(LookAheadState.NULL),
                                 position=asrt.equals(3),
                                 remaining_source=asrt.equals(''))
             ),
            ('x\ny', 'x',
             assert_token_stream(head_token=assert_plain('y'),
                                 look_ahead_state=asrt.is_not(LookAheadState.NULL),
                                 position=asrt.equals(2),
                                 remaining_source=asrt.equals('y'))
             ),
            ('x\n y', 'x',
             assert_token_stream(head_token=assert_plain('y'),
                                 look_ahead_state=asrt.is_not(LookAheadState.NULL),
                                 position=asrt.equals(2),
                                 remaining_source=asrt.equals(' y'))
             ),
            # Multiple tokens
            ('a A', 'a A',
             assert_token_stream(is_null=asrt.is_true,
                                 look_ahead_state=asrt.is_(LookAheadState.NULL),
                                 position=asrt.equals(3),
                                 remaining_source=asrt.equals(''))
             ),
            ('a A\nb B', 'a A',
             assert_token_stream(head_token=assert_plain('b'),
                                 look_ahead_state=asrt.is_not(LookAheadState.NULL),
                                 position=asrt.equals(4),
                                 remaining_source=asrt.equals('b B'))
             ),
            # No tokens
            ('', '',
             assert_token_stream(is_null=asrt.is_true,
                                 look_ahead_state=asrt.is_(LookAheadState.NULL),
                                 position=asrt.equals(0),
                                 remaining_source=asrt.equals(''))
             ),
            (' ', ' ',
             assert_token_stream(is_null=asrt.is_true,
                                 look_ahead_state=asrt.is_(LookAheadState.NULL),
                                 position=asrt.equals(1),
                                 remaining_source=asrt.equals(''))
             ),
            (' \n', ' ',
             assert_token_stream(is_null=asrt.is_true,
                                 look_ahead_state=asrt.is_(LookAheadState.NULL),
                                 position=asrt.equals(2),
                                 remaining_source=asrt.equals(''))
             ),
            (' \n ', ' ',
             assert_token_stream(is_null=asrt.is_true,
                                 look_ahead_state=asrt.is_(LookAheadState.NULL),
                                 position=asrt.equals(2),
                                 remaining_source=asrt.equals(' '))
             ),

        ]
        for source, expected_consumed_string, token_stream_assertion in test_cases:
            with self.subTest(msg=repr(source)):
                ts = sut.TokenStream(source)
                # ACT #
                actual_consumed_string = ts.consume_remaining_part_of_current_line_as_plain_string()
                # ASSERT #
                self.assertEqual(expected_consumed_string,
                                 actual_consumed_string,
                                 'consumed string')
                token_stream_assertion.apply_with_message(self, ts, 'token stream after parse')


class TestMisc(unittest.TestCase):
    def test_remaining_part_of_current_line(self):
        test_cases = [
            ('a', 'a'),
            ('b ', 'b '),
            ('c  ', 'c  '),
            ('d\n_', 'd'),
            ('d  \n_', 'd  '),
        ]
        for source, expected in test_cases:
            with self.subTest(msg=repr(source)):
                ts = sut.TokenStream(source)
                actual = ts.remaining_part_of_current_line
                self.assertEqual(expected, actual)

    def test_remaining_part_of_current_line_after_consumption_of_first_token(self):
        test_cases = [
            ('a', ''),
            ('b ', ''),
            ('c  ', ' '),
            ('a\n_', ''),
            ('a b', 'b'),
            ('d b\n_', 'b'),
        ]
        for source, expected in test_cases:
            with self.subTest(msg=repr(source)):
                ts = sut.TokenStream(source)
                ts.consume()
                actual = ts.remaining_part_of_current_line
                self.assertEqual(expected, actual)
