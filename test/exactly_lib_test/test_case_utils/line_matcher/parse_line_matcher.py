import re
import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher as sut
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherRegex, LineMatcherConstant, \
    LineMatcherNot, LineMatcherAnd, LineMatcherOr
from exactly_lib.test_case_utils.line_matcher.resolvers import LineMatcherConstantResolver
from exactly_lib.util.symbol_table import singleton_symbol_table_2, SymbolTable
from exactly_lib_test.named_element.test_resources.line_matcher import is_line_matcher_reference_to
from exactly_lib_test.named_element.test_resources.named_elem_utils import container
from exactly_lib_test.section_document.parser_implementations.test_resources.token_stream_assertions import \
    assert_token_stream
from exactly_lib_test.section_document.parser_implementations.test_resources.token_stream_parser_prime \
    import remaining_source
from exactly_lib_test.test_case_utils.expression.test_resources import \
    NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_case_utils.line_matcher.test_resources import argument_syntax
from exactly_lib_test.test_case_utils.line_matcher.test_resources.resolver_assertions import \
    resolved_value_equals_line_matcher
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes, surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRegexParser),
        unittest.makeSuite(TestParseLineMatcher),
    ])


class Expectation:
    def __init__(self,
                 resolver: asrt.ValueAssertion,
                 token_stream: asrt.ValueAssertion = asrt.anything_goes()):
        self.resolver = resolver
        self.token_stream = token_stream


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


class TestParseLineMatcher(unittest.TestCase):
    def _check(self,
               source: TokenParserPrime,
               expectation: Expectation):
        # ACT #
        actual_resolver = sut.parse_line_matcher_from_token_parser(source)
        # ASSERT #
        expectation.resolver.apply_with_message(self,
                                                actual_resolver,
                                                'resolver')
        expectation.token_stream.apply_with_message(self,
                                                    source.token_stream,
                                                    'token stream')

    def test_failing_parse(self):
        cases = [
            (
                'neither a symbol, nor a matcher',
                remaining_source(NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME),
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_line_matcher_from_token_parser(source)

    def test_reference(self):
        # ARRANGE #
        symbol = NameAndValue('the_symbol_name',
                              LineMatcherConstant(True))

        symbols = singleton_symbol_table_2(symbol.name,
                                           container(LineMatcherConstantResolver(symbol.value)))

        # ACT & ASSERT #
        self._check(
            remaining_source(symbol.name),
            Expectation(
                resolver=resolved_value_equals_line_matcher(
                    value=symbol.value,
                    references=asrt.matches_sequence([is_line_matcher_reference_to(symbol.name)]),
                    symbols=symbols
                ),
            ))

    def test_not(self):
        # ARRANGE #
        symbol = NameAndValue('the_symbol_name',
                              LineMatcherConstant(True))

        symbols = singleton_symbol_table_2(symbol.name,
                                           container(LineMatcherConstantResolver(symbol.value)))

        # ACT & ASSERT #
        self._check(
            remaining_source('{not_} {symbol}'.format(not_=sut.NOT_OPERATOR_NAME,
                                                      symbol=symbol.name)),
            Expectation(
                resolver=resolved_value_equals_line_matcher(
                    value=LineMatcherNot(symbol.value),
                    references=asrt.matches_sequence([is_line_matcher_reference_to(symbol.name)]),
                    symbols=symbols
                ),
            ))

    def test_and(self):
        # ARRANGE #
        symbol_1 = NameAndValue('the_symbol_1_name',
                                LineMatcherConstant(True))

        symbol_2 = NameAndValue('the_symbol_2_name',
                                LineMatcherConstant(False))

        symbols = SymbolTable({
            symbol_1.name: container(LineMatcherConstantResolver(symbol_1.value)),
            symbol_2.name: container(LineMatcherConstantResolver(symbol_2.value)),
        })

        # ACT & ASSERT #
        self._check(
            remaining_source('{symbol_1} {and_op} {symbol_2}'.format(
                symbol_1=symbol_1.name,
                and_op=sut.AND_OPERATOR_NAME,
                symbol_2=symbol_2.name,
            )),
            Expectation(
                resolver=resolved_value_equals_line_matcher(
                    value=LineMatcherAnd([symbol_1.value,
                                          symbol_2.value]),
                    references=asrt.matches_sequence([
                        is_line_matcher_reference_to(symbol_1.name),
                        is_line_matcher_reference_to(symbol_2.name),
                    ]),
                    symbols=symbols
                ),
            ))

    def test_or(self):
        # ARRANGE #
        symbol_1 = NameAndValue('the_symbol_1_name',
                                LineMatcherConstant(True))

        symbol_2 = NameAndValue('the_symbol_2_name',
                                LineMatcherConstant(False))

        symbols = SymbolTable({
            symbol_1.name: container(LineMatcherConstantResolver(symbol_1.value)),
            symbol_2.name: container(LineMatcherConstantResolver(symbol_2.value)),
        })

        # ACT & ASSERT #
        self._check(
            remaining_source('{symbol_1} {or_op} {symbol_2}'.format(
                symbol_1=symbol_1.name,
                or_op=sut.OR_OPERATOR_NAME,
                symbol_2=symbol_2.name,
            )),
            Expectation(
                resolver=resolved_value_equals_line_matcher(
                    value=LineMatcherOr([symbol_1.value,
                                         symbol_2.value]),
                    references=asrt.matches_sequence([
                        is_line_matcher_reference_to(symbol_1.name),
                        is_line_matcher_reference_to(symbol_2.name),
                    ]),
                    symbols=symbols
                ),
            ))

    def test_regex(self):
        # ARRANGE #
        regex_str = 'regex'

        # ACT & ASSERT #
        self._check(
            remaining_source(argument_syntax.syntax_for_regex_matcher(regex_str)),
            Expectation(
                resolver=resolved_value_is_regex_matcher(regex_str)),
        )


def resolved_value_is_regex_matcher(regex_str: str,
                                    references: asrt.ValueAssertion = asrt.is_empty_list) -> asrt.ValueAssertion:
    expected_matcher = regex_matcher(regex_str)
    return resolved_value_equals_line_matcher(expected_matcher,
                                              references=references)


def regex_matcher(regex_str: str) -> LineMatcherRegex:
    return LineMatcherRegex(re.compile(regex_str))
