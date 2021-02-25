import unittest
from typing import Callable

from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.parse.token import QuoteType, SOFT_QUOTE_CHAR
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import MultiSourceExpectation, \
    Expectation, ParseExpectation, arrangement_w_tcds
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_full_line_expr_parse__s__nsc
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as string_source_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources import integration_check
from exactly_lib_test.impls.types.string_source.test_resources import parse_check
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx, \
    StringSourceOfHereDocAbsStx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.symbol.test_resources.symbol_syntax import A_VALID_SYMBOL_NAME
from exactly_lib_test.test_resources.source.abstract_syntax_impls import OptionallyOnNewLine
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_rest
from exactly_lib_test.type_val_deps.types.string_.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string_.test_resources import here_doc
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_source.test_resources import references
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenariosWithConstantContents),
        unittest.makeSuite(TestSymbolReferences),
        unittest.makeSuite(TestInvalidSyntax),
    ])


class TestSuccessfulScenariosWithConstantContents(unittest.TestCase):
    def test_string(self):
        # ARRANGE #
        string_value = str_abs_stx.StringLiteralAbsStx('the_string_value')
        string_source_syntax = string_source_abs_stx.StringSourceOfStringAbsStx(string_value)
        # ACT & ASSERT #
        CHECKER.check__abs_stx__layouts__std_source_variants__wo_input(
            self,
            OptionallyOnNewLine(string_source_syntax),
            arrangement_w_tcds(),
            MultiSourceExpectation.of_prim__const(
                asrt_string_source.pre_post_freeze__matches_str__const(
                    string_value.value,
                    may_depend_on_external_resources=False,
                )
            )
        )

    def test_empty_string(self):
        # ARRANGE #
        string_value = str_abs_stx.StringLiteralAbsStx.empty_string()
        string_source_syntax = string_source_abs_stx.StringSourceOfStringAbsStx(string_value)
        # ACT & ASSERT #
        CHECKER.check__abs_stx__layouts__std_source_variants__wo_input(
            self,
            OptionallyOnNewLine(string_source_syntax),
            arrangement_w_tcds(),
            MultiSourceExpectation.of_prim__const(
                asrt_string_source.pre_post_freeze__matches_str__const(
                    string_value.value,
                    may_depend_on_external_resources=False,
                )
            )
        )

    def test_sym_ref_syntax_within_hard_quotes(self):
        # ARRANGE #
        string_value = str_abs_stx.StringLiteralAbsStx(
            symbol_syntax.symbol_reference_syntax_for_name(A_VALID_SYMBOL_NAME),
            QuoteType.HARD
        )
        string_source_syntax = string_source_abs_stx.StringSourceOfStringAbsStx(string_value)
        # ACT & ASSERT #
        CHECKER.check__abs_stx__layouts__std_source_variants__wo_input(
            self,
            OptionallyOnNewLine(string_source_syntax),
            arrangement_w_tcds(),
            MultiSourceExpectation.of_prim__const(
                asrt_string_source.pre_post_freeze__matches_str__const(
                    string_value.value,
                    may_depend_on_external_resources=False,
                )
            )
        )

    def test_string__here_doc_start_within_quoted(self):
        # ARRANGE #
        string_value = str_abs_stx.StringLiteralAbsStx(here_doc.here_doc_start_token('MARKER'),
                                                       quoting_=QuoteType.SOFT)
        string_source_syntax = string_source_abs_stx.StringSourceOfStringAbsStx(string_value)
        # ACT & ASSERT #
        CHECKER.check__abs_stx__layouts__std_source_variants__wo_input(
            self,
            OptionallyOnNewLine(string_source_syntax),
            arrangement_w_tcds(),
            MultiSourceExpectation.of_prim__const(
                asrt_string_source.pre_post_freeze__matches_str__const(
                    string_value.value,
                    may_depend_on_external_resources=False,
                )
            )
        )

    def test_here_doc(self):
        # ARRANGE #
        string_value = str_abs_stx.StringHereDocAbsStx('single line in here doc\n')
        string_source_syntax = string_source_abs_stx.StringSourceOfHereDocAbsStx(string_value)
        CHECKER.check__abs_stx__layouts__source_variants__wo_input(
            self,
            equivalent_source_variants__for_full_line_expr_parse__s__nsc,
            OptionallyOnNewLine(string_source_syntax),
            arrangement_w_tcds(),
            MultiSourceExpectation.of_prim__const(
                asrt_string_source.pre_post_freeze__matches_str__const(
                    string_value.value,
                    may_depend_on_external_resources=False,
                )
            )
        )

    def test_here_doc__transformed(self):
        # ARRANGE #
        str_added_by_transformer = '<string added by transformer>'
        transformer_symbol = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER',
            string_transformers.add(str_added_by_transformer),
        )

        here_doc_value = str_abs_stx.StringHereDocAbsStx('single line in here doc\n')
        value_after_transformation = here_doc_value.value + str_added_by_transformer

        string_source_syntax = string_source_abs_stx.TransformedStringSourceAbsStx(
            string_source_abs_stx.StringSourceOfHereDocAbsStx(here_doc_value),
            transformer_symbol.abstract_syntax,
        )

        CHECKER.check__abs_stx__layouts__source_variants__wo_input(
            self,
            equivalent_source_variants__for_full_line_expr_parse__s__nsc,
            OptionallyOnNewLine(string_source_syntax),
            arrangement_w_tcds(
                symbols=transformer_symbol.symbol_table,
            ),
            MultiSourceExpectation.of_prim__const(
                symbol_references=transformer_symbol.references_assertion,
                primitive=asrt_string_source.pre_post_freeze__matches_str__const(
                    value_after_transformation,
                    may_depend_on_external_resources=False,
                )
            )
        )


class TestSymbolReferences(unittest.TestCase):
    def test_just_symbol_reference(self):
        contents_symbol = StringConstantSymbolContext(
            'contents_symbol_name',
            'symbol value contents',
            default_restrictions=asrt_rest.is__w_str_rendering(),
        )

        string_source_syntax = StringSourceOfStringAbsStx(
            str_abs_stx.StringSymbolAbsStx(contents_symbol.name)
        )

        CHECKER.check__abs_stx(
            self,
            string_source_syntax,
            None,
            arrangement_w_tcds(
                symbols=contents_symbol.symbol_table,
            ),
            Expectation.of_prim__const(
                primitive=asrt_string_source.pre_post_freeze__matches_str__const(
                    contents_symbol.str_value,
                    may_depend_on_external_resources=False),
                parse=ParseExpectation(
                    symbol_references=asrt.matches_singleton_sequence(
                        references.is_reference_to__string_source_or_string(contents_symbol.name)
                    ),
                ),
            )
        )

    def test_symbol_reference_in_string__middle(self):
        string_value_template = 'pre symbol {symbol} post symbol'

        def symbol_value_2_expected_contents(symbol_value: str) -> str:
            return string_value_template.format(symbol=symbol_value)

        def symbol_ref_syntax_2_contents_arguments(syntax: str) -> StringSourceAbsStx:
            string_value = string_value_template.format(symbol=syntax)
            return StringSourceOfStringAbsStx(
                str_abs_stx.StringLiteralAbsStx(string_value, QuoteType.SOFT)
            )

        self._test_symbol_reference_in_contents(symbol_ref_syntax_2_contents_arguments,
                                                symbol_value_2_expected_contents)

    def test_symbol_reference_in_string__first(self):
        string_value_template = '{symbol} post symbol'

        def symbol_value_2_expected_contents(symbol_value: str) -> str:
            return string_value_template.format(symbol=symbol_value)

        def symbol_ref_syntax_2_contents_arguments(syntax: str) -> StringSourceAbsStx:
            string_value = string_value_template.format(symbol=syntax)
            return StringSourceOfStringAbsStx(
                str_abs_stx.StringLiteralAbsStx(string_value, QuoteType.SOFT)
            )

        self._test_symbol_reference_in_contents(symbol_ref_syntax_2_contents_arguments,
                                                symbol_value_2_expected_contents)

    def test_symbol_reference_in_here_document(self):
        here_doc_line_template = 'pre symbol {symbol} post symbol'

        def symbol_value_2_expected_contents(symbol_value: str) -> str:
            return here_doc_line_template.format(symbol=symbol_value) + '\n'

        def symbol_ref_syntax_2_contents_arguments(syntax: str) -> StringSourceAbsStx:
            return StringSourceOfHereDocAbsStx(
                str_abs_stx.StringHereDocAbsStx.of_lines__wo_new_lines([
                    here_doc_line_template.format(symbol=syntax)
                ])
            )

        self._test_symbol_reference_in_contents(symbol_ref_syntax_2_contents_arguments,
                                                symbol_value_2_expected_contents)

    def _test_symbol_reference_in_contents(
            self,
            symbol_ref_syntax_2_contents_arguments: Callable[[str], StringSourceAbsStx],
            symbol_value_2_expected_contents: Callable[[str], str]
    ):
        contents_symbol = StringConstantSymbolContext(
            'contents_symbol_name',
            'contents symbol value',
            default_restrictions=asrt_rest.is__w_str_rendering(),
        )

        expected_contents = symbol_value_2_expected_contents(contents_symbol.str_value)

        symbols = [contents_symbol]
        expected_symbol_references = SymbolContext.references_assertion_of_contexts(symbols)
        symbol_table = SymbolContext.symbol_table_of_contexts(symbols)

        string_source_syntax = symbol_ref_syntax_2_contents_arguments(
            symbol_reference_syntax_for_name(contents_symbol.name))

        CHECKER.check__abs_stx(
            self,
            string_source_syntax,
            None,
            arrangement_w_tcds(
                symbols=symbol_table,
            ),
            Expectation.of_prim__const(
                primitive=asrt_string_source.pre_post_freeze__matches_str__const(
                    expected_contents,
                    may_depend_on_external_resources=False),
                parse=ParseExpectation(
                    symbol_references=expected_symbol_references,
                ),
            )
        )


class TestInvalidSyntax(unittest.TestCase):
    def test_fail_when_missing_end_quote(self):
        # ARRANGE #
        string_w_missing_end_quote = StringSourceOfStringAbsStx(
            str_abs_stx.StringLiteralAbsStx(SOFT_QUOTE_CHAR + 'contents')
        )
        # ACT & ASSERT #
        parse_check.checker().check_invalid_syntax__abs_stx(
            self,
            string_w_missing_end_quote
        )


CHECKER = integration_check.checker__w_arbitrary_file_relativities()
