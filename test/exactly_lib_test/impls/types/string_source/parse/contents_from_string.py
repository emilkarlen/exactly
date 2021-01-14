import unittest
from typing import Callable

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.parse.token import QuoteType, SOFT_QUOTE_CHAR
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import MultiSourceExpectation, \
    Expectation, ParseExpectation, arrangement_w_tcds
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as string_source_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources import integration_check
from exactly_lib_test.impls.types.string_source.test_resources import parse_check
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.source.abstract_syntax_impls import OptionallyOnNewLine
from exactly_lib_test.type_val_deps.data.test_resources import concrete_restriction_assertion as asrt_rest
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntax as string_abs_stx
from exactly_lib_test.type_val_deps.types.string.test_resources import here_doc
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import StringAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenariosWithConstantContents),
        unittest.makeSuite(TestSymbolReferences),
        unittest.makeSuite(TestInvalidSyntax),
    ])


class TestSuccessfulScenariosWithConstantContents(unittest.TestCase):
    def test_string(self):
        # ARRANGE #
        string_value = string_abs_stx.StringLiteralAbsStx('the_string_value')
        string_source_syntax = string_source_abs_stx.StringSourceOfStringAbsStx(string_value)
        # ACT & ASSERT #
        CHECKER.check__abs_stx__wo_input__std_layouts_and_source_variants(
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
        string_value = string_abs_stx.StringLiteralAbsStx(here_doc.here_doc_start_token('MARKER'),
                                                          quoting_=QuoteType.SOFT)
        string_source_syntax = string_source_abs_stx.StringSourceOfStringAbsStx(string_value)
        # ACT & ASSERT #
        CHECKER.check__abs_stx__wo_input__std_layouts_and_source_variants(
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
        string_value = string_abs_stx.StringHereDocAbsStx('single line in here doc\n')
        string_source_syntax = string_source_abs_stx.StringSourceOfStringAbsStx(string_value)
        CHECKER.check__abs_stx__wo_input__std_layouts_and_source_variants__full_line_parse(
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


class TestSymbolReferences(unittest.TestCase):
    def test_just_symbol_reference(self):
        contents_symbol = StringConstantSymbolContext(
            'contents_symbol_name',
            'symbol value contents',
            default_restrictions=asrt_rest.is_any_data_type_reference_restrictions(),
        )

        string_source_syntax = StringSourceOfStringAbsStx(
            string_abs_stx.StringSymbolAbsStx(contents_symbol.name)
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
                    symbol_references=contents_symbol.references_assertion,
                ),
            )
        )

    def test_symbol_reference_in_string(self):
        string_value_template = 'pre symbol {symbol} post symbol'

        def symbol_value_2_expected_contents(symbol_value: str) -> str:
            return string_value_template.format(symbol=symbol_value)

        def symbol_ref_syntax_2_contents_arguments(syntax: str) -> StringAbsStx:
            string_value = string_value_template.format(symbol=syntax)
            return string_abs_stx.StringLiteralAbsStx(string_value, QuoteType.SOFT)

        self._test_symbol_reference_in_contents(symbol_ref_syntax_2_contents_arguments,
                                                symbol_value_2_expected_contents)

    def test_symbol_reference_in_here_document(self):
        here_doc_line_template = 'pre symbol {symbol} post symbol'

        def symbol_value_2_expected_contents(symbol_value: str) -> str:
            return here_doc_line_template.format(symbol=symbol_value) + '\n'

        def symbol_ref_syntax_2_contents_arguments(syntax: str) -> StringAbsStx:
            return string_abs_stx.StringHereDocAbsStx.of_lines__wo_new_lines([
                here_doc_line_template.format(symbol=syntax)
            ])

        self._test_symbol_reference_in_contents(symbol_ref_syntax_2_contents_arguments,
                                                symbol_value_2_expected_contents)

    def _test_symbol_reference_in_contents(
            self,
            symbol_ref_syntax_2_contents_arguments: Callable[[str], StringAbsStx],
            symbol_value_2_expected_contents: Callable[[str], str]
    ):
        contents_symbol = StringConstantSymbolContext(
            'contents_symbol_name',
            'contents symbol value',
            default_restrictions=asrt_rest.is_any_data_type_reference_restrictions(),
        )

        expected_contents = symbol_value_2_expected_contents(contents_symbol.str_value)

        symbols = [contents_symbol]
        expected_symbol_references = SymbolContext.references_assertion_of_contexts(symbols)
        symbol_table = SymbolContext.symbol_table_of_contexts(symbols)

        contents_arguments = symbol_ref_syntax_2_contents_arguments(
            symbol_reference_syntax_for_name(contents_symbol.name))

        string_source_syntax = StringSourceOfStringAbsStx(contents_arguments)

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
        string_w_missing_end_quote = string_abs_stx.StringLiteralAbsStx(SOFT_QUOTE_CHAR + 'contents')
        # ACT & ASSERT #
        parse_check.checker().check_invalid_syntax__abs_stx(
            self,
            string_w_missing_end_quote
        )


CHECKER = integration_check.checker__w_arbitrary_file_relativities()
