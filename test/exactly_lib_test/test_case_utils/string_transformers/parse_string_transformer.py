import unittest

import re
from typing import Iterable

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.logic_value_resolver import LogicValueResolver
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherRegex
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer as sut
from exactly_lib.test_case_utils.string_transformer.resolvers import StringTransformerConstant
from exactly_lib.test_case_utils.string_transformer.transformers import ReplaceStringTransformer, \
    SelectStringTransformer
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.string_transformer import SequenceStringTransformer, CustomStringTransformer
from exactly_lib.util.symbol_table import singleton_symbol_table_2, SymbolTable
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_assertions import \
    assert_token_stream
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_parser \
    import remaining_source
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.expression.test_resources import \
    NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_case_utils.line_matcher.test_resources.argument_syntax import syntax_for_regex_matcher
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_case_utils.string_transformers.test_resources.argument_syntax import \
    syntax_for_replace_transformer, syntax_for_sequence_of_transformers, syntax_for_select_transformer
from exactly_lib_test.test_case_utils.string_transformers.test_resources.resolver_assertions import \
    resolved_value_equals_string_transformer
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes, surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestReplaceParser),
        unittest.makeSuite(TestSelectParser),
        unittest.makeSuite(TestParseLineTransformer),
    ])


class Expectation:
    def __init__(self,
                 resolver: ValueAssertion,
                 token_stream: ValueAssertion = asrt.anything_goes()):
        self.resolver = resolver
        self.token_stream = token_stream


class TestReplaceParser(unittest.TestCase):
    def _check(self,
               source: TokenParser,
               expectation: Expectation):
        # ACT #
        actual_resolver = sut.parse_replace(source)
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
                'single REGEX argument (missing REPLACEMENT)',
                remaining_source('regex'),
            ),
            (
                'single REGEX argument (missing REPLACEMENT), but it appears on the following line',
                remaining_source('regex',
                                 ['replacement']),
            ),
            (
                'invalid REGEX',
                remaining_source('** replacement'),
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_replace(source)

    def test_successful_parse_of_unquoted_tokens(self):
        # ARRANGE #
        regex_str = 'regex'
        replacement_str = 'replacement'

        text_on_following_line = 'text on following line'

        expected_resolver = resolved_value_is_replace_transformer(regex_str,
                                                                  replacement_str)
        cases = [
            SourceCase(
                'transformer is only source',
                source=
                remaining_source('{regex} {replacement}'.format(
                    regex=regex_str,
                    replacement=replacement_str,
                )),
                source_assertion=
                assert_token_stream(is_null=asrt.is_true),
            ),
            SourceCase(
                'transformer is followed by a token',
                source=
                remaining_source('{regex} {replacement} following_token'.format(
                    regex=regex_str,
                    replacement=replacement_str,
                )),
                source_assertion=
                assert_token_stream(
                    is_null=asrt.is_false,
                    remaining_part_of_current_line=asrt.equals('following_token')),
            ),
            SourceCase(
                'transformer is only element on current line, but followed by more lines',
                source=
                remaining_source('{regex} {replacement}'.format(
                    regex=regex_str,
                    replacement=replacement_str),
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
        replacement_str = 'the replacement'

        text_on_following_line = 'text on following line'

        expected_resolver = resolved_value_is_replace_transformer(regex_str,
                                                                  replacement_str)
        cases = [
            SourceCase(
                'soft quotes',

                source=
                remaining_source('{regex} {replacement}'.format(
                    regex=surrounded_by_soft_quotes(regex_str),
                    replacement=surrounded_by_soft_quotes(replacement_str),
                )),

                source_assertion=
                assert_token_stream(is_null=asrt.is_true),
            ),
            SourceCase(
                'hard quotes, and text on following line',

                source=
                remaining_source('{regex} {replacement}'.format(
                    regex=surrounded_by_hard_quotes(regex_str),
                    replacement=surrounded_by_hard_quotes(replacement_str),
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


class TestSelectParser(unittest.TestCase):
    def _check(self,
               source: TokenParser,
               expectation: Expectation):
        # ACT #
        actual_resolver = sut.parse_select(source)
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
                'argument is not a line matcher',
                remaining_source('not_a_line_matcher'),
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_replace(source)

    def test_successful_parse_with_regex_matcher(self):
        # ARRANGE #
        regex_str = 'regex'

        text_on_following_line = 'text on following line'

        expected_resolver = resolved_value_is_select_regex_transformer(regex_str)
        cases = [
            SourceCase(
                'transformer is only source',
                source=
                remaining_source(syntax_for_regex_matcher(regex_str)),
                source_assertion=
                assert_token_stream(is_null=asrt.is_true),
            ),
            SourceCase(
                'transformer is followed by a token',
                source=
                remaining_source('{regex_matcher} following_token'.format(
                    regex_matcher=syntax_for_regex_matcher(regex_str),
                )),
                source_assertion=
                assert_token_stream(
                    is_null=asrt.is_false,
                    remaining_part_of_current_line=asrt.equals('following_token')),
            ),
            SourceCase(
                'transformer is only element on current line, but followed by more lines',
                source=
                remaining_source(syntax_for_regex_matcher(regex_str),
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


class TestParseLineTransformer(unittest.TestCase):
    def _check(self,
               source: TokenParser,
               expectation: Expectation):
        # ACT #
        actual_resolver = sut.parse_string_transformer_from_token_parser(source)
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
                'neither a symbol, nor a transformer',
                remaining_source(NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME),
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_replace(source)

    def test_reference(self):
        # ARRANGE #
        symbol = NameAndValue('the_symbol_name',
                              CustomStringTransformerTestImpl())

        symbols = singleton_symbol_table_2(symbol.name,
                                           container(StringTransformerConstant(symbol.value)))

        # ACT & ASSERT #
        self._check(
            remaining_source(symbol.name),
            Expectation(
                resolver=resolved_value_equals_string_transformer(
                    value=symbol.value,
                    references=asrt.matches_sequence([is_reference_to_string_transformer(symbol.name)]),
                    symbols=symbols
                ),
            ))

    def test_replace(self):
        # ARRANGE #
        regex_str = 'regex'
        replacement_str = 'replacement'

        # ACT & ASSERT #
        self._check(
            remaining_source(syntax_for_replace_transformer(regex_str,
                                                            replacement_str)),
            Expectation(
                resolver=resolved_value_is_replace_transformer(
                    regex_str,
                    replacement_str)),
        )

    def test_select(self):
        # ARRANGE #
        regex_str = 'regex'

        # ACT & ASSERT #
        self._check(
            remaining_source(syntax_for_select_transformer(syntax_for_regex_matcher(regex_str))),
            Expectation(
                resolver=resolved_value_is_select_transformer(
                    LineMatcherRegex(re.compile(regex_str)))),
        )

    def test_sequence(self):
        # ARRANGE #
        symbol_1 = NameAndValue('symbol_1_name',
                                CustomStringTransformerTestImpl())
        symbol_2 = NameAndValue('symbol_2_name',
                                CustomStringTransformerTestImpl())

        regex_str = 'regex'
        replacement_str = 'replacement'

        the_replace_transformer = replace_transformer(regex_str,
                                                      replacement_str)
        replace_transformer_syntax = syntax_for_replace_transformer(regex_str,
                                                                    replacement_str)

        arguments = syntax_for_sequence_of_transformers([
            symbol_1.name,
            replace_transformer_syntax,
            symbol_2.name,
        ])
        # ACT & ASSERT #
        self._check(
            remaining_source(arguments),
            Expectation(
                resolver=resolved_value_equals_string_transformer(
                    SequenceStringTransformer([
                        symbol_1.value,
                        the_replace_transformer,
                        symbol_2.value,
                    ]),
                    references=asrt.matches_sequence([
                        is_reference_to_string_transformer(symbol_1.name),
                        is_reference_to_string_transformer(symbol_2.name),
                    ]),
                    symbols=SymbolTable({
                        symbol_1.name: container(StringTransformerConstant(symbol_1.value)),
                        symbol_2.name: container(StringTransformerConstant(symbol_2.value)),
                    }),
                )),
        )


def resolved_value_is_replace_transformer(regex_str: str,
                                          replacement_str: str,
                                          references: ValueAssertion = asrt.is_empty_sequence
                                          ) -> ValueAssertion[LogicValueResolver]:
    expected_transformer = replace_transformer(regex_str, replacement_str)
    return resolved_value_equals_string_transformer(expected_transformer,
                                                    references=references)


def replace_transformer(regex_str: str, replacement_str: str) -> ReplaceStringTransformer:
    return ReplaceStringTransformer(re.compile(regex_str),
                                    replacement_str)


def resolved_value_is_select_regex_transformer(regex_str: str,
                                               references: ValueAssertion = asrt.is_empty_sequence
                                               ) -> ValueAssertion[LogicValueResolver]:
    expected_transformer = select_regex_transformer(regex_str)
    return resolved_value_equals_string_transformer(expected_transformer,
                                                    references=references)


def resolved_value_is_select_transformer(line_matcher: LineMatcher,
                                         references: ValueAssertion = asrt.is_empty_sequence
                                         ) -> ValueAssertion[LogicValueResolver]:
    expected_transformer = select_transformer(line_matcher)
    return resolved_value_equals_string_transformer(expected_transformer,
                                                    references=references)


def select_regex_transformer(regex_str: str) -> SelectStringTransformer:
    return select_transformer(LineMatcherRegex(re.compile(regex_str)))


def select_transformer(line_matcher: LineMatcher) -> SelectStringTransformer:
    return SelectStringTransformer(line_matcher)


class CustomStringTransformerTestImpl(CustomStringTransformer):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        raise NotImplementedError('should not be used')
