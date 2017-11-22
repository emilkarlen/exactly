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
        unittest.makeSuite(TestParseWithoutIgnoreCaseOption),
        unittest.makeSuite(TestParseWithIgnoreCaseOption),
    ])


class Expectation:
    def __init__(self,
                 pattern_string: str,
                 matching_string_list: list,
                 non_matching_string: str,
                 token_stream: asrt.ValueAssertion = asrt.anything_goes()):
        self.pattern_string = pattern_string
        self.non_matching_string = non_matching_string
        self.matching_string_list = matching_string_list
        self.token_stream = token_stream


class TestParseWithoutIgnoreCaseOption(unittest.TestCase):
    def _check(self,
               source: TokenParserPrime,
               expectation: Expectation):
        _check(self, source, expectation)

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

    def test_successful_parse_of_unquoted_tokens(self):
        # ARRANGE #
        regex_str = 'a.*regex'

        text_on_following_line = 'text on following line'

        def _arg(format_string: str) -> str:
            return format_string.format(
                regex=regex_str)

        cases = [
            SourceCase(
                'REG-EX is only source',
                source=
                remaining_source(_arg('{regex}')),
                source_assertion=
                assert_token_stream(is_null=asrt.is_true),
            ),
            SourceCase(
                'REG-EX is followed by a token',
                source=
                remaining_source(_arg('{regex} following_token')),
                source_assertion=
                assert_token_stream(
                    is_null=asrt.is_false,
                    remaining_part_of_current_line=asrt.equals('following_token')),
            ),
            SourceCase(
                'REG-EX is only element on current line, but followed by more lines',
                source=
                remaining_source(_arg('{regex}'),
                                 following_lines=[text_on_following_line]),
                source_assertion=
                assert_token_stream(
                    is_null=asrt.is_false,
                    remaining_part_of_current_line=asrt.equals(''),
                    remaining_source=asrt.equals('\n' + text_on_following_line)),
            ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                self._check(case.source,
                            Expectation(regex_str,
                                        ['aBCregex'],
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
                            Expectation(regex_str,
                                        [' regex'],
                                        ' REGEX',
                                        case.source_assertion))


class TestParseWithIgnoreCaseOption(unittest.TestCase):
    def _check(self,
               source: TokenParserPrime,
               expectation: Expectation):
        _check(self, source, expectation)

    def test_failing_parse(self):
        cases = [
            (
                'missing REG-EX string',
                remaining_source(sut.IGNORE_CASE_OPTION),
            ),
            (
                'no REG-EX argument, but it appears on the following line',
                remaining_source(sut.IGNORE_CASE_OPTION,
                                 ['regex']),
            ),
            (
                'invalid REG-EX',
                remaining_source('{option} {invalid_reg_ex}'.format(
                    option=sut.IGNORE_CASE_OPTION,
                    invalid_reg_ex='**'
                )),
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_regex(source)

    def test_successful_parse_of_unquoted_tokens(self):
        # ARRANGE #
        regex_str = 'a.*regex'

        text_on_following_line = 'text on following line'

        def _arg(format_string: str) -> str:
            return format_string.format(
                option=sut.IGNORE_CASE_OPTION,
                regex=regex_str)

        cases = [
            SourceCase(
                'REG-EX is only source',
                source=
                remaining_source(_arg('{option} {regex}')),
                source_assertion=
                assert_token_stream(is_null=asrt.is_true),
            ),
            SourceCase(
                'REG-EX is followed by a token',
                source=
                remaining_source(_arg('{option} {regex} following_token')),
                source_assertion=
                assert_token_stream(
                    is_null=asrt.is_false,
                    remaining_part_of_current_line=asrt.equals('following_token')),
            ),
            SourceCase(
                'REG-EX is only element on current line, but followed by more lines',
                source=
                remaining_source(_arg('{option} {regex}'),
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
                            Expectation(regex_str,
                                        ['aBCregex', 'AbcREGEX'],
                                        'other',
                                        case.source_assertion))

    def test_successful_parse_of_quoted_tokens(self):
        # ARRANGE #
        regex_str = '.* regex'

        text_on_following_line = 'text on following line'

        cases = [
            SourceCase(
                'soft quotes',

                source=
                remaining_source('{option} {regex}'.format(
                    option=sut.IGNORE_CASE_OPTION,
                    regex=surrounded_by_soft_quotes(regex_str),
                )),

                source_assertion=
                assert_token_stream(is_null=asrt.is_true),
            ),
            SourceCase(
                'hard quotes, and text on following line',

                source=
                remaining_source('{option} {regex}'.format(
                    option=sut.IGNORE_CASE_OPTION,
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
                            Expectation(regex_str,
                                        [' regex', ' REGEX'],
                                        ' rrr',
                                        case.source_assertion))


def _check(put: unittest.TestCase,
           source: TokenParserPrime,
           expectation: Expectation):
    # ACT #
    actual_reg_ex = sut.parse_regex(source)
    # ASSERT #
    expectation.token_stream.apply_with_message(put,
                                                source.token_stream,
                                                'token stream')
    put.assertEqual(expectation.pattern_string,
                    actual_reg_ex.pattern,
                    'regex pattern string')
    for matching_string in expectation.matching_string_list:
        put.assertTrue(bool(actual_reg_ex.search(matching_string)),
                       'reg-ex should match "{}"'.format(matching_string))

    put.assertFalse(bool(actual_reg_ex.search(expectation.non_matching_string)),
                    'reg-ex should not match "{}"'.format(expectation.non_matching_string))
