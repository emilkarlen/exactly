import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import AnyDataTypeRestriction
from exactly_lib.symbol.data.string_resolver import StringFragmentResolver, \
    StringResolver
from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib.symbol.symbol_syntax import SymbolWithReferenceSyntax, \
    symbol_reference_syntax_for_name, \
    constant, symbol, Fragment
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.parse import parse_string as sut
from exactly_lib.util.parse.token import HARD_QUOTE_CHAR, SOFT_QUOTE_CHAR
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_assertions import \
    assert_token_stream, \
    assert_token_string_is
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.data.test_resources.concrete_value_assertions import equals_string_resolver
from exactly_lib_test.test_case_utils.parse.test_resources.invalid_source_tokens import TOKENS_WITH_INVALID_SYNTAX
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailWhenNoArgument),
        unittest.makeSuite(TestParseFragmentsFromToken),
        unittest.makeSuite(TestParseStringResolver),
        unittest.makeSuite(TestParseFromParseSource),
    ])


class Expectation:
    def __init__(self,
                 fragments: list,
                 token_stream: asrt.ValueAssertion):
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

    def test_missing_argument__parse_string_resolver(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_string_resolver(TokenStream(''))


def successful_parse_of_constant() -> list:
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
        TC(_src('"double quoted word" plain-word2'),
           Expectation(
               fragments=[constant('double quoted word')],
               token_stream=assert_token_stream(head_token=assert_token_string_is('plain-word2')),
           )
           ),
        TC(_src('\'single quoted word\' plain-word2'),
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


def successful_parse_of_single_symbol() -> list:
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


def successful_parse_of_complex_structure() -> list:
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

    def test_successful_parse_of_complex_structure(self):
        cases = successful_parse_of_complex_structure()
        for tc in cases:
            self._test_case(tc)


class TestParseStringResolver(unittest.TestCase):
    def _test_case(self, tc: TC):
        with self.subTest(token_stream=tc.source_string):
            # ARRANGE #
            token_stream = TokenStream(tc.source_string)
            # ACT #
            actual = sut.parse_string_resolver(token_stream, CONFIGURATION)
            # ASSERT #
            assertion_on_result = assert_equals_string_resolver(tc.expectation.fragments)
            assertion_on_result.apply_with_message(self, actual, 'fragment')
            tc.expectation.token_stream.apply_with_message(self, token_stream, 'token_stream')

    def test_missing_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_string_resolver(TokenStream(''))

    def test_successful_parse_of_single_symbol(self):
        cases = successful_parse_of_single_symbol()
        for tc in cases:
            self._test_case(tc)

    def test_successful_parse_of_constant(self):
        cases = successful_parse_of_constant()
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
                    sut.parse_string_resolver_from_parse_source(source, CONFIGURATION)

    def test_missing_argument(self):
        parse_source = remaining_source('')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_string_resolver_from_parse_source(parse_source, CONFIGURATION)

    def test_successful_parse(self):
        # ARRANGE #
        symbol_ref = SymbolWithReferenceSyntax('validSymbol_name_1')
        single_symbol = [symbol(symbol_ref.name)]
        parse_source = ParseSource(_src('{soft_quote}{symbol_reference}{soft_quote} rest',
                                        soft_quote=SOFT_QUOTE_CHAR,
                                        symbol_reference=symbol_ref))
        # ACT #
        actual = sut.parse_string_resolver_from_parse_source(parse_source)
        # ASSERT #
        assertion_on_result = assert_equals_string_resolver(single_symbol)
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


def _multi_line_source(lines: list,
                       **kwargs) -> TokenStream:
    all_lines = '\n'.join([_src(line, **kwargs) for line in lines])
    return TokenStream(all_lines)


def assert_equals_string_resolver(fragments: list) -> asrt.ValueAssertion:
    expected_resolver = string_resolver_from_fragments(fragments)
    return equals_string_resolver(expected_resolver)


def string_resolver_from_fragments(fragments: list) -> StringResolver:
    fragment_resolves = [fragment_resolver_from_fragment(f) for f in fragments]
    return StringResolver(tuple(fragment_resolves))


def fragment_resolver_from_fragment(fragment: Fragment) -> StringFragmentResolver:
    if fragment.is_constant:
        return string_resolvers.str_fragment(fragment.value)
    else:
        sr = SymbolReference(fragment.value,
                             ReferenceRestrictionsOnDirectAndIndirect(direct=AnyDataTypeRestriction(),
                                                                      indirect=None))
        return string_resolvers.symbol_fragment(sr)


def single_symbol_reference(symbol_name: str,
                            reference_restrictions: ReferenceRestrictions = None) -> sut.StringResolver:
    if reference_restrictions is None:
        reference_restrictions = no_restrictions()
    fragments = (string_resolvers.symbol_fragment(SymbolReference(symbol_name,
                                                                  reference_restrictions)),)
    return sut.StringResolver(fragments)


def no_restrictions() -> ReferenceRestrictions:
    return ReferenceRestrictionsOnDirectAndIndirect(direct=AnyDataTypeRestriction())
