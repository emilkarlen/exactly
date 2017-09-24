import re
import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherRegex
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer as sut
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant
from exactly_lib.test_case_utils.lines_transformer.transformers import ReplaceLinesTransformer, \
    CustomLinesTransformer, SequenceLinesTransformer, SelectLinesTransformer
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.util.symbol_table import singleton_symbol_table_2, SymbolTable
from exactly_lib_test.section_document.parser_implementations.test_resources.token_stream_assertions import \
    assert_token_stream
from exactly_lib_test.section_document.parser_implementations.test_resources.token_stream_parser_prime \
    import remaining_source
from exactly_lib_test.symbol.test_resources.lines_transformer import is_lines_transformer_reference_to
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.expression.test_resources import \
    NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_case_utils.line_matcher.test_resources.argument_syntax import syntax_for_regex_matcher
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.argument_syntax import \
    syntax_for_replace_transformer, syntax_for_sequence_of_transformers, syntax_for_select_transformer
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.resolver_assertions import \
    resolved_value_equals_lines_transformer
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes, surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestReplaceParser),
        unittest.makeSuite(TestSelectParser),
        unittest.makeSuite(TestParseLineTransformer),
    ])


class Expectation:
    def __init__(self,
                 resolver: asrt.ValueAssertion,
                 token_stream: asrt.ValueAssertion = asrt.anything_goes()):
        self.resolver = resolver
        self.token_stream = token_stream


class TestReplaceParser(unittest.TestCase):
    def _check(self,
               source: TokenParserPrime,
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
               source: TokenParserPrime,
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
               source: TokenParserPrime,
               expectation: Expectation):
        # ACT #
        actual_resolver = sut.parse_lines_transformer_from_token_parser(source)
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
                              CustomLinesTransformerTestImpl())

        symbols = singleton_symbol_table_2(symbol.name,
                                           container(LinesTransformerConstant(symbol.value)))

        # ACT & ASSERT #
        self._check(
            remaining_source(symbol.name),
            Expectation(
                resolver=resolved_value_equals_lines_transformer(
                    value=symbol.value,
                    references=asrt.matches_sequence([is_lines_transformer_reference_to(symbol.name)]),
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
                                CustomLinesTransformerTestImpl())
        symbol_2 = NameAndValue('symbol_2_name',
                                CustomLinesTransformerTestImpl())

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
                resolver=resolved_value_equals_lines_transformer(
                    SequenceLinesTransformer([
                        symbol_1.value,
                        the_replace_transformer,
                        symbol_2.value,
                    ]),
                    references=asrt.matches_sequence([
                        is_lines_transformer_reference_to(symbol_1.name),
                        is_lines_transformer_reference_to(symbol_2.name),
                    ]),
                    symbols=SymbolTable({
                        symbol_1.name: container(LinesTransformerConstant(symbol_1.value)),
                        symbol_2.name: container(LinesTransformerConstant(symbol_2.value)),
                    }),
                )),
        )


def resolved_value_is_replace_transformer(regex_str: str,
                                          replacement_str: str,
                                          references: asrt.ValueAssertion = asrt.is_empty_list) -> asrt.ValueAssertion:
    expected_transformer = replace_transformer(regex_str, replacement_str)
    return resolved_value_equals_lines_transformer(expected_transformer,
                                                   references=references)


def replace_transformer(regex_str: str, replacement_str: str) -> ReplaceLinesTransformer:
    return ReplaceLinesTransformer(re.compile(regex_str),
                                   replacement_str)


def resolved_value_is_select_regex_transformer(regex_str: str,
                                               references: asrt.ValueAssertion = asrt.is_empty_list) -> asrt.ValueAssertion:
    expected_transformer = select_regex_transformer(regex_str)
    return resolved_value_equals_lines_transformer(expected_transformer,
                                                   references=references)


def resolved_value_is_select_transformer(line_matcher: LineMatcher,
                                         references: asrt.ValueAssertion = asrt.is_empty_list) -> asrt.ValueAssertion:
    expected_transformer = select_transformer(line_matcher)
    return resolved_value_equals_lines_transformer(expected_transformer,
                                                   references=references)


def select_regex_transformer(regex_str: str) -> SelectLinesTransformer:
    return select_transformer(LineMatcherRegex(re.compile(regex_str)))


def select_transformer(line_matcher: LineMatcher) -> SelectLinesTransformer:
    return SelectLinesTransformer(line_matcher)


class CustomLinesTransformerTestImpl(CustomLinesTransformer):
    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        raise NotImplementedError('should not be used')
