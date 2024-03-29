import itertools
import unittest
from typing import List

from exactly_lib.definitions.test_case import reserved_words
from exactly_lib.impls.types.string_ import parse_string as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.element_parsers.token_stream_parser import ParserFromTokens, TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference, ReferenceRestrictions, SymbolDependentValue, SymbolName
from exactly_lib.symbol.symbol_syntax import SymbolWithReferenceSyntax, \
    symbol_reference_syntax_for_name, \
    constant, symbol, Fragment
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import \
    ArbitraryValueWStrRenderingRestriction
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_deps.types.string_.string_sdv import StringFragmentSdv, \
    StringSdv
from exactly_lib.util.either import Either
from exactly_lib.util.parse.token import HARD_QUOTE_CHAR, SOFT_QUOTE_CHAR
from exactly_lib_test.impls.types.parse.test_resources.invalid_source_tokens import TOKENS_WITH_INVALID_SYNTAX
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_assertions import \
    assert_token_stream, \
    assert_token_string_is
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase, MessageBuilder
from exactly_lib_test.type_val_deps.types.string_.test_resources.sdv_assertions import equals_string_sdv


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailWhenNoArgument),
        unittest.makeSuite(TestFailWhenHeadIsReservedToken),
        unittest.makeSuite(TestParseFragmentsFromToken),
        unittest.makeSuite(TestParseStringSdvAndParseSymRefOrStringSdv),
        unittest.makeSuite(TestParseFromParseSource),
    ])


class Expectation:
    def __init__(self,
                 fragments: List[Fragment],
                 token_stream: Assertion):
        self.fragments = fragments
        self.token_stream = token_stream


class TC:
    def __init__(self,
                 source_string: str,
                 expectation: Expectation):
        self.source_string = source_string
        self.expectation = expectation


class TestFailWhenNoArgument(unittest.TestCase):
    def test_missing_argument__parse_fragments_from_token(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_fragments_from_tokens(TokenStream(''))

    def test_missing_argument__parse_string_sdv(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_string_sdv(TokenStream(''))


class TestFailWhenHeadIsReservedToken(unittest.TestCase):
    def test_parse_fragments_from_token(self):
        for reserved in reserved_words.RESERVED_TOKENS:
            with self.subTest(reserved):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_fragments_from_tokens(TokenStream(reserved))

    def test_parse_string_sdv(self):
        for reserved in reserved_words.RESERVED_TOKENS:
            with self.subTest(reserved):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_string_sdv(TokenStream(reserved))


def successful_parse_of_constant() -> List[TC]:
    return [
        TC(_src('plain-word1 plain-word2'),
           Expectation(
               fragments=[constant('plain-word1')],
               token_stream=assert_token_stream(head_token=assert_token_string_is('plain-word2')),
           )
           ),
        TC(_src('word'),
           Expectation(
               fragments=[constant('word')],
               token_stream=assert_token_stream(is_null=asrt.is_true),
           )
           ),
        TC(_src('{soft_quote}double quoted word{soft_quote} plain-word2',
                soft_quote=SOFT_QUOTE_CHAR),
           Expectation(
               fragments=[constant('double quoted word')],
               token_stream=assert_token_stream(head_token=assert_token_string_is('plain-word2')),
           )
           ),
        TC(_src('{hard_quote}single quoted word{hard_quote} plain-word2',
                hard_quote=HARD_QUOTE_CHAR),
           Expectation(
               fragments=[constant('single quoted word')],
               token_stream=assert_token_stream(head_token=assert_token_string_is('plain-word2')),
           )
           ),
        TC(_src('{hard_quote}{symbol_reference}{hard_quote} plain-word2',
                symbol_reference=symbol_reference_syntax_for_name('sym_name'),
                hard_quote=HARD_QUOTE_CHAR),
           Expectation(
               fragments=[constant(symbol_reference_syntax_for_name('sym_name'))],
               token_stream=assert_token_stream(head_token=assert_token_string_is('plain-word2')),
           )
           ),
    ]


def successful_parse_of_quoted_reserved_tokens() -> List[TC]:
    def cases_for_word(reserved: str) -> List[TC]:
        return [
            TC(_src('{hard_quote}{reserved}{hard_quote}',
                    hard_quote=HARD_QUOTE_CHAR,
                    reserved=reserved),
               Expectation(
                   fragments=[constant(reserved)],
                   token_stream=assert_token_stream(is_null=asrt.is_true),
               )
               ),
            TC(_src('{hard_quote}{reserved}{hard_quote} plain-word2',
                    hard_quote=HARD_QUOTE_CHAR,
                    reserved=reserved),
               Expectation(
                   fragments=[constant(reserved)],
                   token_stream=assert_token_stream(head_token=assert_token_string_is('plain-word2')),
               )
               ),
            TC(_src('{soft_quote}{reserved}{soft_quote} plain-word2',
                    soft_quote=SOFT_QUOTE_CHAR,
                    reserved=reserved),
               Expectation(
                   fragments=[constant(reserved)],
                   token_stream=assert_token_stream(head_token=assert_token_string_is('plain-word2')),
               )
               ),
        ]

    return list(
        itertools.chain.from_iterable([
            cases_for_word(word)
            for word in reserved_words.RESERVED_TOKENS
        ])
    )


def successful_parse_of_single_symbol() -> List[TC]:
    symbol_ref = SymbolWithReferenceSyntax('validSymbol_name_1')
    single_symbol = [symbol(symbol_ref.name)]
    return [
        TC(_src('{symbol_reference}',
                symbol_reference=symbol_ref),
           Expectation(
               fragments=single_symbol,
               token_stream=assert_token_stream(is_null=asrt.is_true),
           )
           ),
        TC(_src('{symbol_reference} rest',
                symbol_reference=symbol_ref),
           Expectation(
               fragments=single_symbol,
               token_stream=assert_token_stream(head_token=assert_token_string_is('rest')),
           )
           ),
        TC(_src('{soft_quote}{symbol_reference}{soft_quote} rest',
                soft_quote=SOFT_QUOTE_CHAR,
                symbol_reference=symbol_ref),
           Expectation(
               fragments=single_symbol,
               token_stream=assert_token_stream(head_token=assert_token_string_is('rest')),
           )
           ),
    ]


def successful_parse_of_complex_structure() -> List[TC]:
    return [
        TC(_src('  {soft_quote}{sym_ref1}const 1{not_a_symbol_name1}{not_a_symbol_name2}const 2{sym_ref2}{soft_quote}',
                soft_quote=SOFT_QUOTE_CHAR,
                sym_ref1=symbol_reference_syntax_for_name('sym_name1'),
                not_a_symbol_name1=symbol_reference_syntax_for_name('not a sym1'),
                not_a_symbol_name2=symbol_reference_syntax_for_name('not a sym2'),
                sym_ref2=symbol_reference_syntax_for_name('sym_name2')),
           Expectation(
               fragments=[symbol('sym_name1'),
                          constant('const 1' +
                                   symbol_reference_syntax_for_name('not a sym1') +
                                   symbol_reference_syntax_for_name('not a sym2') +
                                   'const 2'),
                          symbol('sym_name2')],
               token_stream=assert_token_stream(is_null=asrt.is_true),
           ))]


class TestParseFragmentsFromToken(unittest.TestCase):
    def _test_case(self, tc: TC):
        with self.subTest(token_stream=tc.source_string):
            # ARRANGE #
            token_stream = TokenStream(tc.source_string)
            # ACT #
            actual = sut.parse_fragments_from_tokens(token_stream, CONFIGURATION)
            # ASSERT #
            self.assertEqual(tc.expectation.fragments, actual, 'fragment')
            tc.expectation.token_stream.apply_with_message(self, token_stream, 'token_stream')

    def test_missing_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_fragments_from_tokens(TokenStream(''))

    def test_successful_parse_of_single_symbol(self):
        cases = successful_parse_of_single_symbol()
        for tc in cases:
            self._test_case(tc)

    def test_successful_parse_of_constant(self):
        cases = successful_parse_of_constant()
        for tc in cases:
            self._test_case(tc)

    def test_successful_parse_of_quoted_reserved_tokens(self):
        cases = successful_parse_of_quoted_reserved_tokens()
        for tc in cases:
            self._test_case(tc)

    def test_successful_parse_of_complex_structure(self):
        cases = successful_parse_of_complex_structure()
        for tc in cases:
            self._test_case(tc)


class TestParseStringSdvAndParseSymRefOrStringSdv(unittest.TestCase):
    def _test_case(self, tc: TC):
        with self.subTest(token_stream=tc.source_string,
                          parser='parse_string_sdv'):
            self._test_case__parse_string_sdv(tc)

        with self.subTest(token_stream=tc.source_string,
                          parser='sym_ref_or_string_parser'):
            parser = sut.SymbolReferenceOrStringParser(CONFIGURATION)
            self._test_case__sym_ref_or_string_parser(parser, tc)

    def _test_case__parse_string_sdv(self, tc: TC):
        # ARRANGE #
        token_stream = TokenStream(tc.source_string)
        # ACT #
        actual = sut.parse_string_sdv(token_stream, CONFIGURATION)
        # ASSERT #
        tc.expectation.token_stream.apply_with_message(self, token_stream, 'token_stream')
        assertion_on_result = assert_equals_string_sdv(tc.expectation.fragments)
        assertion_on_result.apply_with_message(self, actual, 'fragment')

    def _test_case__sym_ref_or_string_parser(self, parser: ParserFromTokens, tc: TC):
        # ARRANGE #
        token_stream = TokenStream(tc.source_string)
        token_parser = TokenParser(token_stream)
        expected_fragments = tc.expectation.fragments
        head_is_plain = TokenStream(tc.source_string).head.is_plain
        assertion_on_value = (
            _EqualsEitherOfSymbolName(expected_fragments[0].value)
            if head_is_plain and len(expected_fragments) == 1 and expected_fragments[0].is_symbol
            else
            _EqualsEitherOfStringSdv(expected_fragments)
        )
        # ACT #
        actual = parser.parse(token_parser)
        # ASSERT #
        tc.expectation.token_stream.apply_with_message(self, token_stream, 'token_stream')
        assertion_on_value.apply_with_message(self, actual, 'fragment')

    def test_missing_argument__parse_string_sdv(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_string_sdv(TokenStream(''))

    def test_missing_argument__parse_sym_ref_or_string_sdv(self):
        parser = sut.SymbolReferenceOrStringParser(CONFIGURATION)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.parse(TokenParser(TokenStream('')))

    def test_successful_parse_of_single_symbol(self):
        cases = successful_parse_of_single_symbol()
        for tc in cases:
            self._test_case(tc)

    def test_successful_parse_of_constant(self):
        cases = successful_parse_of_constant()
        for tc in cases:
            self._test_case(tc)

    def test_successful_parse_of_quoted_reserved_tokens(self):
        cases = successful_parse_of_quoted_reserved_tokens()
        for tc in cases:
            self._test_case(tc)

    def test_successful_parse_of_complex_structure(self):
        cases = successful_parse_of_complex_structure()
        for tc in cases:
            self._test_case(tc)


class TestParseFromParseSource(unittest.TestCase):
    def test_raise_exception_for_invalid_argument_syntax_when_invalid_quoting_of_first_token(self):
        for case in TOKENS_WITH_INVALID_SYNTAX:
            with self.subTest(name=case.name,
                              source=case.value):
                source = remaining_source(case.value)
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_string_sdv_from_parse_source(source, CONFIGURATION)

    def test_missing_argument(self):
        parse_source = remaining_source('')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_string_sdv_from_parse_source(parse_source, CONFIGURATION)

    def test_successful_parse(self):
        # ARRANGE #
        symbol_ref = SymbolWithReferenceSyntax('validSymbol_name_1')
        single_symbol = [symbol(symbol_ref.name)]
        parse_source = ParseSource(_src('{soft_quote}{symbol_reference}{soft_quote} rest',
                                        soft_quote=SOFT_QUOTE_CHAR,
                                        symbol_reference=symbol_ref))
        # ACT #
        actual = sut.parse_string_sdv_from_parse_source(parse_source)
        # ASSERT #
        assertion_on_result = assert_equals_string_sdv(single_symbol)
        assertion_on_result.apply_with_message(self, actual, 'result')
        assertion_on_parse_source = assert_source(remaining_part_of_current_line=asrt.equals('rest'))
        assertion_on_parse_source.apply_with_message(self, parse_source, 'parse_source')


CONFIGURATION = sut.Configuration('string-arg')


def _src(s: str,
         **kwargs) -> str:
    return s.format(**kwargs)


def _single_line_source(s: str,
                        **kwargs) -> TokenStream:
    return TokenStream(_src(s, **kwargs))


def _multi_line_source(lines: List[str],
                       **kwargs) -> TokenStream:
    all_lines = '\n'.join([_src(line, **kwargs) for line in lines])
    return TokenStream(all_lines)


def assert_equals_string_sdv(fragments: List[Fragment]) -> Assertion[SymbolDependentValue]:
    expected_sdv = string_sdv_from_fragments(fragments)
    return equals_string_sdv(expected_sdv)


def string_sdv_from_fragments(fragments: List[Fragment]) -> StringSdv:
    fragment_resolves = [fragment_sdv_from_fragment(f) for f in fragments]
    return StringSdv(tuple(fragment_resolves))


def fragment_sdv_from_fragment(fragment: Fragment) -> StringFragmentSdv:
    if fragment.is_constant:
        return string_sdvs.str_fragment(fragment.value)
    else:
        sr = SymbolReference(fragment.value,
                             ReferenceRestrictionsOnDirectAndIndirect(
                                 direct=ArbitraryValueWStrRenderingRestriction.of_any(),
                                 indirect=None)
                             )
        return string_sdvs.symbol_fragment(sr)


def single_symbol_reference(symbol_name: str,
                            reference_restrictions: ReferenceRestrictions = None) -> StringSdv:
    if reference_restrictions is None:
        reference_restrictions = no_restrictions()
    fragments = (string_sdvs.symbol_fragment(SymbolReference(symbol_name,
                                                             reference_restrictions)),)
    return sut.StringSdv(fragments)


def no_restrictions() -> ReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(direct=ArbitraryValueWStrRenderingRestriction.of_any(),
                                                    indirect=None)


class _EqualsEitherOfSymbolName(AssertionBase[Either[SymbolName, StringSdv]]):
    def __init__(self, expected_symbol_name: str):
        self._expected_symbol_name = expected_symbol_name

    def _apply(self,
               put: unittest.TestCase,
               value: Either[SymbolName, StringSdv],
               message_builder: MessageBuilder,
               ):
        put.assertTrue(value.is_left(),
                       message_builder.apply('form of Either')
                       )
        put.assertEqual(self._expected_symbol_name,
                        value.left(),
                        message_builder.apply('value of Either (left SymbolName)')
                        )


class _EqualsEitherOfStringSdv(AssertionBase[Either[SymbolName, StringSdv]]):
    def __init__(self, expected_fragments: List[Fragment]):
        self._expected_fragments = expected_fragments

    def _apply(self,
               put: unittest.TestCase,
               value: Either[SymbolName, StringSdv],
               message_builder: MessageBuilder,
               ):
        put.assertTrue(value.is_right(),
                       message_builder.apply('form of Either')
                       )
        assertion_on_sdv = assert_equals_string_sdv(self._expected_fragments)
        assertion_on_sdv.apply(
            put,
            value.right(),
            message_builder.for_sub_component('sdv')
        )
