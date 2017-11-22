import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case_utils.parse import parse_reg_ex as sut
from exactly_lib_test.section_document.parser_implementations.test_resources.token_stream_assertions import \
    assert_token_stream
from exactly_lib_test.section_document.parser_implementations.test_resources.token_stream_parser_prime \
    import remaining_source
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes, surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestSuccessfulParse),
    ])


class Expectation:
    def __init__(self,
                 matching_string: str,
                 non_matching_string: str,
                 token_stream: asrt.ValueAssertion = asrt.anything_goes()):
        self.non_matching_string = non_matching_string
        self.matching_string = matching_string
        self.token_stream = token_stream


class TestFailingParse(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            (
                'no arguments',
                remaining_source(''),
            ),
            (
                'no arguments, but it appears on the following line',
                remaining_source('',
                                 ['regex']),
            ),
            (
                'invalid REGEX',
                remaining_source('**'),
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_regex(source)


class TestSuccessfulParse(unittest.TestCase):
    def _check(self,
               source: TokenParserPrime,
               expectation: Expectation):
        # ACT #
        actual_reg_ex = sut.parse_regex(source)
        # ASSERT #
        expectation.token_stream.apply_with_message(self,
                                                    source.token_stream,
                                                    'token stream')
        self.assertTrue(bool(actual_reg_ex.search(expectation.matching_string)),
                        'reg-ex should match "{}"'.format(expectation.matching_string))

        self.assertFalse(bool(actual_reg_ex.search(expectation.non_matching_string)),
                         'reg-ex should not match "{}"'.format(expectation.non_matching_string))

    def test_successful_parse_of_unquoted_tokens(self):
        # ARRANGE #
        regex_str = 'a.*regex'

        text_on_following_line = 'text on following line'

        cases = [
            SourceCase(
                'transformer is only source',
                source=
                remaining_source('{regex}'.format(
                    regex=regex_str,
                )),
                source_assertion=
                assert_token_stream(is_null=asrt.is_true),
            ),
            SourceCase(
                'transformer is followed by a token',
                source=
                remaining_source('{regex} following_token'.format(
                    regex=regex_str,
                )),
                source_assertion=
                assert_token_stream(
                    is_null=asrt.is_false,
                    remaining_part_of_current_line=asrt.equals('following_token')),
            ),
            SourceCase(
                'transformer is only element on current line, but followed by more lines',
                source=
                remaining_source('{regex}'.format(
                    regex=regex_str,
                ),
                    following_lines=[text_on_following_line]),
                source_assertion=
                assert_token_stream(
                    is_null=asrt.is_false,
                    remaining_source=asrt.equals('\n' + text_on_following_line)),
            ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                self._check(case.source,
                            Expectation('aBCregex',
                                        'AbcREGEX',
                                        case.source_assertion))

    def test_successful_parse_of_quoted_tokens(self):
        # ARRANGE #
        regex_str = '.* regex'

        text_on_following_line = 'text on following line'

        cases = [
            SourceCase(
                'soft quotes',

                source=
                remaining_source('{regex}'.format(
                    regex=surrounded_by_soft_quotes(regex_str),
                )),

                source_assertion=
                assert_token_stream(is_null=asrt.is_true),
            ),
            SourceCase(
                'hard quotes, and text on following line',

                source=
                remaining_source('{regex}'.format(
                    regex=surrounded_by_hard_quotes(regex_str),
                ),
                    following_lines=[text_on_following_line]),

                source_assertion=
                assert_token_stream(
                    remaining_source=asrt.equals('\n' + text_on_following_line)),
            ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                self._check(case.source,
                            Expectation(' regex',
                                        ' REGEX',
                                        case.source_assertion))
