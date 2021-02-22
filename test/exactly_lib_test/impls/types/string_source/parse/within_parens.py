import unittest

from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import MultiSourceExpectation, \
    Expectation, ParseExpectation, arrangement_w_tcds
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_full_line_expr_parse__s__nsc
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as string_source_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources import integration_check
from exactly_lib_test.impls.types.string_source.test_resources import parse_check
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx
from exactly_lib_test.test_resources.source.abstract_syntax_impls import OptionallyOnNewLine, WithinParensAbsStx, \
    CustomAbsStx
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.test_resources.data import data_restrictions_assertions as asrt_rest
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValidSyntax),
        unittest.makeSuite(TestInvalidSyntax),
    ])


class TestValidSyntax(unittest.TestCase):
    def test_string_symbol(self):
        contents_symbol = StringConstantSymbolContext(
            'contents_symbol_name',
            'symbol value contents',
            default_restrictions=asrt_rest.is_reference_restrictions__convertible_to_string(),
        )

        string_source_syntax = StringSourceOfStringAbsStx(
            str_abs_stx.StringSymbolAbsStx(contents_symbol.name)
        )

        CHECKER.check__abs_stx(
            self,
            OptionallyOnNewLine(WithinParensAbsStx(string_source_syntax)),
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

    def test_here_doc(self):
        # ARRANGE #
        string_value = str_abs_stx.StringHereDocAbsStx('single line in here doc\n')
        string_source_syntax = string_source_abs_stx.StringSourceOfStringAbsStx(string_value)
        CHECKER.check__abs_stx__layouts__source_variants__wo_input(
            self,
            equivalent_source_variants__for_full_line_expr_parse__s__nsc,
            OptionallyOnNewLine(WithinParensAbsStx(string_source_syntax,
                                                   end_paren_on_separate_line=True)),
            arrangement_w_tcds(),
            MultiSourceExpectation.of_prim__const(
                asrt_string_source.pre_post_freeze__matches_str__const(
                    string_value.value,
                    may_depend_on_external_resources=False,
                )
            )
        )


class TestInvalidSyntax(unittest.TestCase):
    def test_fail_when_missing_end_end_paren(self):
        # ARRANGE #
        valid_string = str_abs_stx.StringLiteralAbsStx('contents')
        missing_end_paren = CustomAbsStx(
            TokenSequence.concat([
                TokenSequence.singleton('('),
                valid_string.tokenization(),
            ])
        )
        # ACT & ASSERT #
        parse_check.checker().check_invalid_syntax__abs_stx(
            self,
            OptionallyOnNewLine(missing_end_paren)
        )


CHECKER = integration_check.checker__w_arbitrary_file_relativities()
