import unittest
from typing import List, Optional

from exactly_lib.impls.types.string_ import parse_string_or_here_doc as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source_lines
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.data.symbol_reference_assertions import \
    equals_symbol_references__convertible_to_string
from exactly_lib_test.type_val_deps.types.string.test_resources import here_doc_assertion_utils as asrt_hd
from exactly_lib_test.type_val_deps.types.string.test_resources import sdv_assertions
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes_str


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestString),
        unittest.makeSuite(TestHereDoc),
    ])


class TestString(unittest.TestCase):
    def test_invalid_syntax(self):
        cases = [
            NameAndValue('missing end quote',
                         [
                             '{soft_quote} some text'.format(soft_quote=SOFT_QUOTE_CHAR),
                         ]),
            # Case with missing  start quote is not handled - it is a bug
            # The lookahead of TokenParser is the cause.
        ]
        for case in cases:
            source = remaining_source_lines(case.value)
            with self.subTest(case_name=case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_string_or_here_doc_from_parse_source(source)

    def test_valid_syntax_without_symbol_references(self):
        single_string_token_value = 'singleStringTokenValue'
        multiple_tokens_string_value = 'multiple tokens string value'
        following_arg_token = 'singleToken'
        cases = [
            NameAndValue('non-quoted string-token on single line',
                         (
                             [
                                 single_string_token_value,
                             ],
                             ExpectedString(single_string_token_value,
                                            CommonExpectation(
                                                symbol_references=[],
                                                source=asrt_source.is_at_end_of_line(1)))
                         )
                         ),
            NameAndValue('non-quoted string-token on following line',
                         (
                             [
                                 '',
                                 single_string_token_value,
                             ],
                             ExpectedString(single_string_token_value,
                                            CommonExpectation(
                                                symbol_references=[],
                                                source=asrt_source.is_at_end_of_line(2)))
                         )
                         ),
            NameAndValue('non-quoted string-token on single line, followed by arguments on same line',
                         (
                             [
                                 '{string_token} {following_argument}'.format(
                                     string_token=single_string_token_value,
                                     following_argument=following_arg_token,
                                 )
                             ],
                             ExpectedString(single_string_token_value,
                                            CommonExpectation(
                                                symbol_references=[],
                                                source=asrt_source.assert_source(
                                                    current_line_number=asrt.equals(1),
                                                    remaining_part_of_current_line=asrt.equals(
                                                        following_arg_token))))
                         )
                         ),
            NameAndValue('quoted string-token on single line',
                         (
                             [
                                 surrounded_by_soft_quotes_str(multiple_tokens_string_value),
                             ],
                             ExpectedString(multiple_tokens_string_value,
                                            CommonExpectation(
                                                symbol_references=[],
                                                source=asrt_source.is_at_end_of_line(1)))
                         )
                         ),
        ]
        for case in cases:
            source_lines, expected_string = case.value
            source = remaining_source_lines(source_lines)
            with self.subTest(case_name=case.name):
                _expect_string(self, source, expected_string)

    def test_valid_syntax_with_symbol_references(self):
        symbol = StringConstantSymbolContext('symbol_name', 'symbol value')
        before_symbol = 'text before symbol'
        after_symbol = 'text after symbol'
        following_arg_token = 'singleToken'
        cases = [
            NameAndValue('single unquoted symbol reference',
                         (
                             [
                                 symbol.name__sym_ref_syntax,
                             ],
                             ExpectedString(symbol.str_value,
                                            CommonExpectation(
                                                symbol_references=[
                                                    symbol.reference__convertible_to_string,
                                                ],
                                                source=asrt_source.is_at_end_of_line(1),
                                                symbol_table=symbol.symbol_table,
                                            )
                                            )
                         )
                         ),
            NameAndValue('single unquoted symbol reference followed by args on same line',
                         (
                             [
                                 '{sym_ref} {following_argument}'.format(
                                     sym_ref=symbol.name__sym_ref_syntax,
                                     following_argument=following_arg_token,
                                 ),
                             ],
                             ExpectedString(symbol.str_value,
                                            CommonExpectation(
                                                symbol_references=[
                                                    symbol.reference__convertible_to_string,
                                                ],
                                                source=asrt_source.assert_source(
                                                    current_line_number=asrt.equals(1),
                                                    remaining_part_of_current_line=asrt.equals(
                                                        following_arg_token)),
                                                symbol_table=symbol.symbol_table,
                                            ),
                                            )
                         )
                         ),
            NameAndValue('reference embedded in quoted string',
                         (
                             [
                                 '{soft_quote}{before_sym_ref}{sym_ref}{after_sym_ref}{soft_quote}'.format(
                                     soft_quote=SOFT_QUOTE_CHAR,
                                     sym_ref=symbol.name__sym_ref_syntax,
                                     before_sym_ref=before_symbol,
                                     after_sym_ref=after_symbol,
                                 )
                             ],
                             ExpectedString(before_symbol + symbol.str_value + after_symbol,
                                            CommonExpectation(
                                                symbol_references=[
                                                    symbol.reference__convertible_to_string,
                                                ],
                                                source=asrt_source.is_at_end_of_line(1),
                                                symbol_table=symbol.symbol_table,
                                            )
                                            )
                         )
                         ),
        ]
        for case in cases:
            source_lines, expected_string = case.value
            source = remaining_source_lines(source_lines)
            with self.subTest(case_name=case.name):
                _expect_string(self, source, expected_string)


class TestHereDoc(unittest.TestCase):
    def test_invalid_syntax(self):
        source = remaining_source_lines(['<<marker',
                                         'contents',
                                         'nonMarker',
                                         ])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse_string_or_here_doc_from_parse_source(source)

    def test_without_symbol_references(self):
        expected_contents_line = 'contents'
        source = remaining_source_lines(['<<MARKER',
                                         expected_contents_line,
                                         'MARKER',
                                         'Line 4',
                                         ])
        expectation = ExpectedHereDoc(
            resolved_here_doc_lines=[expected_contents_line],
            common=CommonExpectation(
                symbol_references=[],
                source=asrt_source.is_at_beginning_of_line(4))

        )
        _expect_here_doc(self, source, expectation)

    def test_without_symbol_references__on_following_line(self):
        expected_contents_line = 'contents'
        source = remaining_source_lines(['',
                                         '<<MARKER',
                                         expected_contents_line,
                                         'MARKER',
                                         'Line 5',
                                         ])
        expectation = ExpectedHereDoc(
            resolved_here_doc_lines=[expected_contents_line],
            common=CommonExpectation(
                symbol_references=[],
                source=asrt_source.is_at_beginning_of_line(5))

        )
        _expect_here_doc(self, source, expectation)

    def test_without_symbol_references__without_following_line(self):
        expected_contents_line = 'contents'
        source = remaining_source_lines(['<<MARKER',
                                         expected_contents_line,
                                         'MARKER',
                                         ])
        expectation = ExpectedHereDoc(
            resolved_here_doc_lines=[expected_contents_line],
            common=CommonExpectation(
                symbol_references=[],
                source=asrt_source.is_at_end_of_line(3))

        )
        _expect_here_doc(self, source, expectation)

    def test_with_symbol_references(self):
        symbol1 = StringConstantSymbolContext('symbol_1_name', 'symbol 1 value')
        line_with_sym_ref_template = 'before symbol {symbol} after symbol'
        source = remaining_source_lines(['<<MARKER',
                                         line_with_sym_ref_template.format(
                                             symbol=symbol1.name__sym_ref_syntax),
                                         'MARKER',
                                         'Line 4',
                                         ]
                                        )
        expectation = ExpectedHereDoc(
            resolved_here_doc_lines=[
                line_with_sym_ref_template.format(
                    symbol=symbol1.str_value)
            ],
            common=CommonExpectation(
                symbol_references=[
                    symbol1.reference__convertible_to_string,
                ],
                symbol_table=symbol1.symbol_table,
                source=asrt_source.is_at_beginning_of_line(4),
            )

        )
        _expect_here_doc(self, source, expectation)


class CommonExpectation:
    def __init__(self,
                 symbol_references: List[SymbolReference],
                 source: Assertion[ParseSource],
                 symbol_table: Optional[SymbolTable] = None):
        self.symbol_references = symbol_references
        self.source = source
        self.symbol_table = empty_symbol_table() if symbol_table is None else symbol_table


class ExpectedString:
    def __init__(self,
                 resolved_str: str,
                 common: CommonExpectation):
        self.resolved_str = resolved_str
        self.common = common


class ExpectedHereDoc:
    def __init__(self,
                 resolved_here_doc_lines: List[str],
                 common: CommonExpectation):
        self.resolved_here_doc_lines = resolved_here_doc_lines
        self.common = common


def _expect_here_doc(put: unittest.TestCase,
                     source: ParseSource,
                     expectation: ExpectedHereDoc):
    # ACT #
    actual = sut.parse_string_or_here_doc_from_parse_source(source,
                                                            consume_last_here_doc_line=True)
    # ASSERT #
    assertion_on_here_doc = asrt_hd.matches_resolved_value(expectation.resolved_here_doc_lines,
                                                           expectation.common.symbol_references,
                                                           expectation.common.symbol_table)
    assertion_on_here_doc.apply_with_message(put, actual,
                                             'here_document')
    _expect_common(put, source, actual,
                   expectation.common)


def _expect_string(put: unittest.TestCase,
                   source: ParseSource,
                   expectation: ExpectedString):
    # ACT #
    actual_sdv = sut.parse_string_or_here_doc_from_parse_source(source)
    # ASSERT #
    assertion_on_here_doc = sdv_assertions.matches_primitive_string(
        asrt.equals(expectation.resolved_str),
        expectation.common.symbol_references,
        expectation.common.symbol_table)
    assertion_on_here_doc.apply_with_message(put, actual_sdv,
                                             'string_sdv')
    _expect_common(put, source, actual_sdv,
                   expectation.common)


def _expect_common(put: unittest.TestCase,
                   actual_source: ParseSource,
                   actual_result: StringSdv,
                   expectation: CommonExpectation):
    symbol_references_assertion = equals_symbol_references__convertible_to_string(expectation.symbol_references)
    symbol_references_assertion.apply_with_message(put, actual_result.references,
                                                   'references')

    expectation.source.apply_with_message(put, actual_source,
                                          'source_after_parse')
