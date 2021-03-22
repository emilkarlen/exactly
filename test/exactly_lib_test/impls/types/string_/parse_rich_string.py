import unittest
from types import MappingProxyType
from typing import List, Optional, NamedTuple, Mapping, Any

from exactly_lib.impls.types.string_ import parse_rich_string as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR, QuoteType
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    SourceStr2SourceVariants, NSourceCase, equivalent_source_variants__for_full_line_expr_parse__s__nsc, \
    equivalent_source_variants__for_expr_parse__s__nsc
from exactly_lib_test.test_resources.source import abs_stx_utils
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.abstract_syntax_impls import OptionallyOnNewLine, CustomAbsStx
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string_.test_resources import here_doc
from exactly_lib_test.type_val_deps.types.string_.test_resources import rich_abstract_syntaxes as abs_stx
from exactly_lib_test.type_val_deps.types.string_.test_resources import sdv_assertions
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.rich_abstract_syntaxes import HereDocAbsStx, \
    TextUntilEndOfLineAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestString),
        unittest.makeSuite(TestTextUntilEndOfLine),
        unittest.makeSuite(TestHereDoc),
    ])


class Arrangement:
    def __init__(self, symbol_table: Optional[SymbolTable] = None):
        self.symbol_table = empty_symbol_table() if symbol_table is None else symbol_table


ARRANGEMENT__NEUTRAL = Arrangement()


class Expectation(NamedTuple):
    symbol_references: List[SymbolReference]
    resolved_str: str


class Variant(NamedTuple):
    name: str
    syntax: AbstractSyntax
    resolved_str: str


class TestString(unittest.TestCase):
    def test_invalid_syntax(self):
        cases = [
            NameAndValue('missing end quote',
                         '{soft_quote} some text'.format(soft_quote=SOFT_QUOTE_CHAR)),
            # Case with missing  start quote is not handled - it is a bug
            # The lookahead of TokenParser is the cause.
        ]
        for case in cases:
            CHECKER.check_invalid_syntax(
                self,
                equivalent_source_variants__for_full_line_expr_parse__s__nsc,
                abs_stx.PlainStringAbsStx(
                    StringLiteralAbsStx(case.value)
                ),
                sub_test_identifiers={
                    'case': case.name,
                }
            )

    def test_valid_syntax_without_symbol_references(self):
        single_string_token_value = 'singleStringTokenValue'
        multiple_tokens_string_value = 'multiple tokens string value'
        multi_line_string = 'string\nspanning multiple \n lines\n'
        cases = [
            Variant(
                'non-quoted string-token on single line',
                StringLiteralAbsStx(single_string_token_value),
                single_string_token_value,
            ),
            Variant(
                'quoted string-token on single line',
                StringLiteralAbsStx(multiple_tokens_string_value, QuoteType.SOFT),
                multiple_tokens_string_value,
            ),
            Variant(
                'quoted multi line string',
                StringLiteralAbsStx(multi_line_string, QuoteType.SOFT),
                multi_line_string,
            ),
        ]
        for variant in cases:
            # ACT & ASSERT #
            CHECKER.check(
                self,
                equivalent_source_variants__for_expr_parse__s__nsc,
                variant.syntax,
                Arrangement(),
                Expectation(
                    [],
                    variant.resolved_str,
                )
            )

    def test_valid_syntax_with_symbol_references(self):
        symbol = StringConstantSymbolContext('symbol_name', 'symbol value')
        before_symbol = 'text before symbol'
        after_symbol = 'text after symbol'
        cases = [
            Variant(
                'single unquoted symbol reference',
                symbol.abstract_syntax,
                symbol.str_value,
            ),
            Variant(
                'reference embedded in quoted string',
                StringLiteralAbsStx('{before_sym_ref}{sym_ref}{after_sym_ref}'.format(
                    sym_ref=symbol.name__sym_ref_syntax,
                    before_sym_ref=before_symbol,
                    after_sym_ref=after_symbol,
                ),
                    QuoteType.SOFT,
                ),
                before_symbol + symbol.str_value + after_symbol,
            ),
        ]
        for variant in cases:
            # ACT & ASSERT #
            CHECKER.check(
                self,
                equivalent_source_variants__for_expr_parse__s__nsc,
                variant.syntax,
                Arrangement(symbol.symbol_table),
                Expectation(
                    [symbol.reference__w_str_rendering],
                    variant.resolved_str,
                )
            )


class TEolCase(NamedTuple):
    name: str
    source: AbstractSyntax
    arrangement: Arrangement
    expectation: Expectation


class TestTextUntilEndOfLine(unittest.TestCase):
    def test(self):
        symbol = StringConstantSymbolContext('symbol_1_name', 'symbol 1 value')
        str_with_space_and_invalid_token_syntax = 'before and after space, ' + SOFT_QUOTE_CHAR + 'after quote'

        cases = [
            TEolCase(
                'no text',
                TextUntilEndOfLineAbsStx(''),
                ARRANGEMENT__NEUTRAL,
                Expectation(
                    [],
                    ''
                )
            ),
            TEolCase(
                'string with one space after marker, and no space at EOL',
                TextUntilEndOfLineAbsStx(str_with_space_and_invalid_token_syntax),
                ARRANGEMENT__NEUTRAL,
                Expectation(
                    [],
                    str_with_space_and_invalid_token_syntax
                )
            ),
            TEolCase(
                'with surrounding space',
                TextUntilEndOfLineAbsStx(
                    '   ' + str_with_space_and_invalid_token_syntax + '  \t '
                ),
                ARRANGEMENT__NEUTRAL,
                Expectation(
                    [],
                    str_with_space_and_invalid_token_syntax
                )
            ),
            TEolCase(
                'with symbol reference',
                TextUntilEndOfLineAbsStx(
                    ''.join(['before',
                             symbol.name__sym_ref_syntax,
                             'after'])
                ),
                Arrangement(
                    symbol.symbol_table
                ),
                Expectation(
                    [symbol.reference__w_str_rendering],
                    ''.join(['before', symbol.str_value, 'after']),
                ),
            ),
        ]
        # ACT & ASSERT #
        for case in cases:
            CHECKER.check(
                self,
                equivalent_source_variants__for_full_line_expr_parse__s__nsc,
                case.source,
                case.arrangement,
                case.expectation,
                sub_test_identifiers={
                    'case': case.name
                }
            )


class TestHereDoc(unittest.TestCase):
    def test_invalid_syntax(self):
        syntax = CustomAbsStx(
            TokenSequence.sequence([
                here_doc.here_doc_start_token('marker'),
                '\n',
                'contents',
                '\n',
                'non_marker',
            ])
        )
        CHECKER.check_invalid_syntax(
            self,
            equivalent_source_variants__for_full_line_expr_parse__s__nsc,
            syntax,
        )

    def test_without_symbol_references(self):
        expected_contents = 'contents\n'
        syntax = HereDocAbsStx(expected_contents)
        CHECKER.check(
            self,
            equivalent_source_variants__for_full_line_expr_parse__s__nsc,
            syntax,
            Arrangement(),
            Expectation(
                [],
                expected_contents
            )
        )

    def test_with_symbol_references(self):
        symbol = StringConstantSymbolContext('symbol_1_name', 'symbol 1 value')
        line_with_sym_ref_template = 'before symbol {symbol} after symbol\n'
        syntax = HereDocAbsStx(
            line_with_sym_ref_template.format(
                symbol=symbol.name__sym_ref_syntax)
        )
        CHECKER.check(
            self,
            equivalent_source_variants__for_full_line_expr_parse__s__nsc,
            syntax,
            Arrangement(symbol.symbol_table),
            Expectation(
                [symbol.reference__w_str_rendering],
                line_with_sym_ref_template.format(
                    symbol=symbol.str_value)
            )
        )


class Checker:
    def __init__(self, parser: Parser[StringSdv]):
        self._parser = parser

    def check_invalid_syntax(self,
                             put: unittest.TestCase,
                             mk_source_variants: SourceStr2SourceVariants,
                             source: AbstractSyntax,
                             sub_test_identifiers: Mapping[str, Any] = MappingProxyType({}),
                             ):
        for formatting_case in abs_stx_utils.formatting_cases(OptionallyOnNewLine(source)):
            for source_case in mk_source_variants(formatting_case.value):
                with put.subTest(zz_source_formatting=formatting_case.name,
                                 zz_source_variant=source_case.name,
                                 **sub_test_identifiers):
                    with put.assertRaises(SingleInstructionInvalidArgumentException):
                        self._parser.parse(source_case.source)

    def check(
            self,
            put: unittest.TestCase,
            mk_source_variants: SourceStr2SourceVariants,
            source: AbstractSyntax,
            arrangement: Arrangement,
            expectation: Expectation,
            sub_test_identifiers: Mapping[str, Any] = MappingProxyType({}),
    ):
        for formatting_case in abs_stx_utils.formatting_cases(OptionallyOnNewLine(source)):
            for source_case in mk_source_variants(formatting_case.value):
                with put.subTest(zz_source_formatting=formatting_case.name,
                                 zz_source_variant=source_case.name,
                                 **sub_test_identifiers):
                    self._act_and_assert(
                        put,
                        source_case,
                        arrangement,
                        expectation,
                    )

    def _act_and_assert(
            self,
            put: unittest.TestCase,
            source_case: NSourceCase,
            arrangement: Arrangement,
            expectation: Expectation,
    ):
        # ACT #
        actual = self._parser.parse(source_case.source)
        # ASSERT #
        put.assertIsInstance(actual, StringSdv, 'object type')
        source_case.expectation.apply_with_message(
            put,
            source_case.source,
            'source after parse',
        )
        assertion_on_value = sdv_assertions.matches_primitive_string(
            asrt.equals(expectation.resolved_str),
            expectation.symbol_references,
            arrangement.symbol_table)
        assertion_on_value.apply_with_message(put, actual, 'parsed object')


CHECKER = Checker(sut.RichStringParser())
