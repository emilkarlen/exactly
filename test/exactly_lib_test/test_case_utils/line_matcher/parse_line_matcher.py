import re
import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.integer.integer_matcher import IntegerMatcher, \
    IntegerMatcherFromComparisonOperator
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher as sut
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherRegex, LineMatcherConstant, \
    LineMatcherNot, LineMatcherAnd, LineMatcherOr, LineMatcherLineNumber
from exactly_lib.test_case_utils.line_matcher.resolvers import LineMatcherConstantResolver
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.util import symbol_table
from exactly_lib_test.section_document.parser_implementations.test_resources.token_stream_assertions import \
    assert_token_stream
from exactly_lib_test.section_document.parser_implementations.test_resources.token_stream_parser_prime \
    import remaining_source
from exactly_lib_test.symbol.test_resources.line_matcher import is_line_matcher_reference_to
from exactly_lib_test.test_case_utils.line_matcher.test_resources import argument_syntax
from exactly_lib_test.test_case_utils.line_matcher.test_resources.resolver_assertions import \
    resolved_value_equals_line_matcher, resolved_value_matches_line_matcher
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_case_utils.test_resources import matcher_parse_check
from exactly_lib_test.test_case_utils.test_resources.matcher_parse_check import Expectation
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.matcher_assertions import is_equivalent_to, ModelInfo
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes, surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRegexParser),
        unittest.makeSuite(TestLineNumberParser),
        unittest.makeSuite(TestParseLineMatcher),
    ])


class Configuration(matcher_parse_check.Configuration):
    def parse(self, parser: TokenParserPrime) -> SymbolValueResolver:
        return sut.parse_line_matcher_from_token_parser(parser)

    def resolved_value_equals(self,
                              value: LineMatcher,
                              references: asrt.ValueAssertion = asrt.is_empty_list,
                              symbols: symbol_table.SymbolTable = None) -> asrt.ValueAssertion:
        return resolved_value_equals_line_matcher(
            value,
            references,
            symbols
        )

    def is_reference_to(self, symbol_name: str) -> asrt.ValueAssertion:
        return is_line_matcher_reference_to(symbol_name)

    def resolver_of_constant_matcher(self, matcher: LineMatcher) -> SymbolValueResolver:
        return LineMatcherConstantResolver(matcher)

    def constant_matcher(self, result: bool) -> LineMatcher:
        return LineMatcherConstant(result)

    def not_matcher(self, matcher: LineMatcher) -> LineMatcher:
        return LineMatcherNot(matcher)

    def and_matcher(self, matchers: list) -> LineMatcher:
        return LineMatcherAnd(matchers)

    def or_matcher(self, matchers: list) -> LineMatcher:
        return LineMatcherOr(matchers)


class TestRegexParser(unittest.TestCase):
    def _check(self,
               source: TokenParserPrime,
               expectation: Expectation):
        # ACT #
        actual_resolver = sut.parse_regex(source)
        # ASSERT #
        expectation.resolver.apply_with_message(self, actual_resolver,
                                                'resolver')
        expectation.token_stream.apply_with_message(self,
                                                    source.token_stream,
                                                    'token stream')

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
        regex_str = 'regex'

        text_on_following_line = 'text on following line'

        expected_resolver = resolved_value_is_regex_matcher(regex_str)
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
                            Expectation(expected_resolver,
                                        case.source_assertion))

    def test_successful_parse_of_quoted_tokens(self):
        # ARRANGE #
        regex_str = 'the regex'

        text_on_following_line = 'text on following line'

        expected_resolver = resolved_value_is_regex_matcher(regex_str)
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
                            Expectation(expected_resolver,
                                        case.source_assertion))


class TestLineNumberParser(unittest.TestCase):
    def _check(self,
               source: TokenParserPrime,
               expectation: Expectation):
        # ACT #
        actual_resolver = sut.parse_line_number(source)
        # ASSERT #
        expectation.resolver.apply_with_message(self, actual_resolver,
                                                'resolver')
        expectation.token_stream.apply_with_message(self,
                                                    source.token_stream,
                                                    'token stream')

    def test_failing_parse(self):
        cases = [
            (
                'no arguments',
                remaining_source(''),
            ),
            (
                'no arguments, but it appears on the following line',
                remaining_source('  ',
                                 ['= 69']),
            ),
            (
                'invalid OPERATOR',
                remaining_source('~ 69'),
            ),
            (
                'invalid INTEGER EXPRESSION',
                remaining_source('~ notAnInteger'),
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_line_number(source)

    def test_successful_parse(self):
        # ARRANGE #
        def model_of(rhs: int) -> ModelInfo:
            return ModelInfo((rhs, 'irrelevant line contents'))

        expected_integer_matcher = IntegerMatcherFromComparisonOperator(sut.LINE_NUMBER_PROPERTY,
                                                                        comparators.LT,
                                                                        69)
        expected_resolver = resolved_value_is_line_number_matcher(expected_integer_matcher,
                                                                  [
                                                                      model_of(60),
                                                                      model_of(69),
                                                                      model_of(72),

                                                                  ])

        text_on_following_line = 'text on following line'

        cases = [
            SourceCase(
                'simple comparison',

                source=
                remaining_source('< 69',
                                 following_lines=[text_on_following_line]),

                source_assertion=
                assert_token_stream(
                    remaining_source=asrt.equals('\n' + text_on_following_line)),
            ),
            SourceCase(
                'following tokens on same line',

                source=
                remaining_source('< 69 next',
                                 following_lines=[text_on_following_line]),

                source_assertion=
                assert_token_stream(
                    remaining_source=asrt.equals('next' + '\n' + text_on_following_line)),
            ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                self._check(case.source,
                            Expectation(expected_resolver,
                                        case.source_assertion))


class TestParseLineMatcher(matcher_parse_check.TestParseStandardExpressionsBase):
    _conf = Configuration()

    @property
    def conf(self) -> Configuration:
        return self._conf

    def test_regex(self):
        # ARRANGE #
        regex_str = 'regex'

        # ACT & ASSERT #
        self._check(
            remaining_source(argument_syntax.syntax_for_regex_matcher(regex_str)),
            Expectation(
                resolver=resolved_value_is_regex_matcher(regex_str)),
        )

    def test_line_number(self):
        # ARRANGE #
        def model_of(rhs: int) -> ModelInfo:
            return ModelInfo((rhs, 'irrelevant line contents'))

        comparator = comparators.LT
        rhs = 72
        expected_integer_matcher = IntegerMatcherFromComparisonOperator(sut.LINE_NUMBER_PROPERTY,
                                                                        comparator,
                                                                        rhs)
        expected_resolver = resolved_value_is_line_number_matcher(expected_integer_matcher,
                                                                  [
                                                                      model_of(69),
                                                                      model_of(72),
                                                                      model_of(80),

                                                                  ])

        # ACT & ASSERT #
        self._check(
            remaining_source(argument_syntax.syntax_for_line_number_matcher(comparator,
                                                                            str(rhs))),
            Expectation(
                resolver=expected_resolver),
        )


def resolved_value_is_regex_matcher(regex_str: str,
                                    references: asrt.ValueAssertion = asrt.is_empty_list) -> asrt.ValueAssertion:
    expected_matcher = regex_matcher(regex_str)
    return resolved_value_equals_line_matcher(expected_matcher,
                                              references=references)


def resolved_value_is_line_number_matcher(integer_matcher: IntegerMatcher,
                                          model_infos: list,
                                          references: asrt.ValueAssertion = asrt.is_empty_list) -> asrt.ValueAssertion:
    expected_matcher = is_equivalent_to(LineMatcherLineNumber(integer_matcher),
                                        model_infos)
    return resolved_value_matches_line_matcher(expected_matcher,
                                               references=references)


def regex_matcher(regex_str: str) -> LineMatcherRegex:
    return LineMatcherRegex(re.compile(regex_str))
