import unittest

from exactly_lib.instructions.utils.arg_parse import parse_string as sut
from exactly_lib.instructions.utils.arg_parse.symbol import SymbolWithReferenceSyntax, symbol_reference_syntax_for_name, \
    constant, symbol, Fragment
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.symbol.concrete_restrictions import NoRestriction
from exactly_lib.symbol.string_resolver import SymbolStringFragmentResolver, StringFragmentResolver, \
    ConstantStringFragmentResolver, StringResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.symbol.value_restriction import ReferenceRestrictions
from exactly_lib.util.parse.token import HARD_QUOTE_CHAR, SOFT_QUOTE_CHAR
from exactly_lib_test.section_document.parser_implementations.test_resources import assert_token_stream2, \
    assert_token_string_is
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.symbol.test_resources.concrete_value_assertions import equals_string_resolver3
from exactly_lib_test.test_resources.parse import remaining_source
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
            sut.parse_fragments_from_token(TokenStream2(''))

    def test_missing_argument__parse_string_resolver(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_string_resolver(TokenStream2(''))


def successful_parse_of_constant() -> list:
    return [
        TC(_src('plain-word1 plain-word2'),
           Expectation(
               fragments=[constant('plain-word1')],
               token_stream=assert_token_stream2(head_token=assert_token_string_is('plain-word2')),
           )
           ),
        TC(_src('word'),
           Expectation(
               fragments=[constant('word')],
               token_stream=assert_token_stream2(is_null=asrt.is_true),
           )
           ),
        TC(_src('"double quoted word" plain-word2'),
           Expectation(
               fragments=[constant('double quoted word')],
               token_stream=assert_token_stream2(head_token=assert_token_string_is('plain-word2')),
           )
           ),
        TC(_src('\'single quoted word\' plain-word2'),
           Expectation(
               fragments=[constant('single quoted word')],
               token_stream=assert_token_stream2(head_token=assert_token_string_is('plain-word2')),
           )
           ),
        TC(_src('{hard_quote}{symbol_reference}{hard_quote} plain-word2',
                symbol_reference=symbol_reference_syntax_for_name('sym_name'),
                hard_quote=HARD_QUOTE_CHAR),
           Expectation(
               fragments=[constant(symbol_reference_syntax_for_name('sym_name'))],
               token_stream=assert_token_stream2(head_token=assert_token_string_is('plain-word2')),
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
               token_stream=assert_token_stream2(is_null=asrt.is_true),
           )
           ),
        TC(_src('{symbol_reference} rest',
                symbol_reference=symbol_ref),
           Expectation(
               fragments=single_symbol,
               token_stream=assert_token_stream2(head_token=assert_token_string_is('rest')),
           )
           ),
        TC(_src('{soft_quote}{symbol_reference}{soft_quote} rest',
                soft_quote=SOFT_QUOTE_CHAR,
                symbol_reference=symbol_ref),
           Expectation(
               fragments=single_symbol,
               token_stream=assert_token_stream2(head_token=assert_token_string_is('rest')),
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
               token_stream=assert_token_stream2(is_null=asrt.is_true),
           ))]


class TestParseFragmentsFromToken(unittest.TestCase):
    def _test_case(self, tc: TC):
        with self.subTest(token_stream=tc.source_string):
            # ARRANGE #
            token_stream = TokenStream2(tc.source_string)
            # ACT #
            actual = sut.parse_fragments_from_token(token_stream, CONFIGURATION)
            # ASSERT #
            self.assertEqual(tc.expectation.fragments, actual, 'fragment')
            tc.expectation.token_stream.apply_with_message(self, token_stream, 'token_stream')

    def test_missing_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_fragments_from_token(TokenStream2(''))

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
            token_stream = TokenStream2(tc.source_string)
            # ACT #
            actual = sut.parse_string_resolver(token_stream, CONFIGURATION)
            # ASSERT #
            assertion_on_result = assert_equals_string_resolver(tc.expectation.fragments)
            assertion_on_result.apply_with_message(self, actual, 'fragment')
            tc.expectation.token_stream.apply_with_message(self, token_stream, 'token_stream')

    def test_missing_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_string_resolver(TokenStream2(''))

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
                        **kwargs) -> TokenStream2:
    return TokenStream2(_src(s, **kwargs))


def _multi_line_source(lines: list,
                       **kwargs) -> TokenStream2:
    all_lines = '\n'.join([_src(line, **kwargs) for line in lines])
    return TokenStream2(all_lines)


def assert_equals_string_resolver(list_of_fragments: list) -> asrt.ValueAssertion:
    fragment_resolves = [fragment_resolver_from_fragment(f) for f in list_of_fragments]
    expected_resolver = StringResolver(tuple(fragment_resolves))
    return equals_string_resolver3(expected_resolver)


def fragment_resolver_from_fragment(fragment: Fragment) -> StringFragmentResolver:
    if fragment.is_constant:
        return ConstantStringFragmentResolver(fragment.value)
    else:
        sr = SymbolReference(fragment.value,
                             ReferenceRestrictions(direct=NoRestriction(),
                                                   every=None))
        return SymbolStringFragmentResolver(sr)


def single_symbol_reference(symbol_name: str,
                            reference_restrictions: ReferenceRestrictions = None) -> sut.StringResolver:
    if reference_restrictions is None:
        reference_restrictions = no_restrictions()
    fragments = (SymbolStringFragmentResolver(SymbolReference(symbol_name,
                                                              reference_restrictions)),)
    return sut.StringResolver(fragments)


def no_restrictions() -> ReferenceRestrictions:
    return ReferenceRestrictions(direct=NoRestriction())
