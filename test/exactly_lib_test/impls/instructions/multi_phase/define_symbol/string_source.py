import unittest
from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.abstract_syntax import \
    DefineSymbolWMandatoryValue
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.embryo_checker import \
    INSTRUCTION_CHECKER, PARSE_CHECKER
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.source_formatting import *
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import Arrangement, Expectation
from exactly_lib_test.impls.types.logic.test_resources import intgr_arr_exp
from exactly_lib_test.impls.types.string_source.test_resources import integration_check as str_src_check
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx, \
    StringSourceOfHereDocAbsStx
from exactly_lib_test.symbol.test_resources import symbol_syntax
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.abstract_syntax_impls import CustomAbsStx
from exactly_lib_test.test_resources.source.custom_abstract_syntax import SequenceAbsStx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources import type_sdv_assertions
from exactly_lib_test.type_val_deps.sym_ref.test_resources.container_assertions import matches_container
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import MISSING_END_QUOTE__SOFT, \
    StringLiteralAbsStx, StringHereDocAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_source.test_resources.symbol_context import \
    StringSourceSymbolContextOfPrimitiveConstant
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenarios),
        unittest.makeSuite(TestUnsuccessfulScenarios),
    ])


class TestSuccessfulScenarios(unittest.TestCase):
    def test_reference_to_string_source(self):
        # ARRANGE #
        defined_name = symbol_syntax.A_VALID_SYMBOL_NAME

        referenced_symbol = StringSourceSymbolContextOfPrimitiveConstant('referenced_name',
                                                                         'contents of string source')
        syntax = _syntax_of(
            referenced_symbol.abstract_syntax,
            defined_name,
        )

        arrangement = Arrangement.phase_agnostic()

        # EXPECTATION #

        expectation = _expect_definition_of(
            defined_name,
            referenced_symbol.symbol_table,
            referenced_symbol.references_assertion,
            referenced_symbol.contents_str,
            may_depend_on_external_resources=False
        )

        # ACT & ASSERT #

        INSTRUCTION_CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            syntax,
            arrangement,
            expectation,
        )

    def test_here_doc_with_embedded_references(self):
        # ARRANGE #
        defined_name = symbol_syntax.A_VALID_SYMBOL_NAME

        here_doc_line_template = 'pre symbol {symbol} post symbol'

        referenced_symbol = StringConstantSymbolContext(
            'REFERENCED_STRING_SYMBOL',
            'contents of string symbol',
            default_restrictions=data_restrictions_assertions.is__w_str_rendering(),
        )
        expected_contents = here_doc_line_template.format(symbol=referenced_symbol.str_value) + '\n'

        syntax = _syntax_of(
            StringSourceOfHereDocAbsStx(
                StringHereDocAbsStx.of_lines__wo_new_lines([
                    here_doc_line_template.format(symbol=referenced_symbol.name__sym_ref_syntax)
                ])
            ),
            defined_name,
        )

        arrangement = Arrangement.phase_agnostic()

        # EXPECTATION #

        expectation = _expect_definition_of(
            defined_name,
            referenced_symbol.symbol_table,
            referenced_symbol.references_assertion,
            expected_contents,
            may_depend_on_external_resources=False
        )

        # ACT & ASSERT #

        INSTRUCTION_CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            syntax,
            arrangement,
            expectation,
        )


class TestUnsuccessfulScenarios(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'missing argument',
                CustomAbsStx.empty(),
            ),
            NameAndValue(
                'missing end quote',
                StringSourceOfStringAbsStx(MISSING_END_QUOTE__SOFT),
            ),
            NameAndValue(
                'superfluous arguments',
                SequenceAbsStx.followed_by_superfluous(
                    StringSourceOfStringAbsStx(StringLiteralAbsStx('valid string', QuoteType.HARD))
                ),
            ),
        ]
        # ARRANGE #
        for case in cases:
            with self.subTest(case.name):
                PARSE_CHECKER.check_invalid_syntax__abs_stx(
                    self,
                    _syntax_of(case.value)
                )


def _syntax_of(string_source: AbstractSyntax,
               defined_name: str = symbol_syntax.A_VALID_SYMBOL_NAME) -> AbstractSyntax:
    return DefineSymbolWMandatoryValue(
        defined_name,
        ValueType.STRING_SOURCE,
        string_source,
    )


def _expect_definition_of(
        defined_name: str,
        symbols_for_evaluation: SymbolTable,
        references: Assertion[Sequence[SymbolReference]],
        expected_contents: str,
        may_depend_on_external_resources: bool,
) -> Expectation[None]:
    sdv_expectation = type_sdv_assertions.matches_sdv(
        asrt.is_instance(StringSourceSdv),
        references=references,
        symbols=symbols_for_evaluation,
        resolved_value=asrt.anything_goes(),
        custom=asrt.is_instance_with(
            StringSourceSdv,
            str_src_check.execution_assertion(
                intgr_arr_exp.Arrangement(
                    symbols=symbols_for_evaluation,
                    tcds=TcdsArrangement(),
                ),
                primitive=str_src_check.primitive__const(
                    asrt_string_source.pre_post_freeze__matches_str__const(
                        expected_contents,
                        may_depend_on_external_resources=may_depend_on_external_resources
                    )
                )
            )
        )
    )
    expected_container = matches_container(
        asrt.equals(ValueType.STRING_SOURCE),
        sdv_expectation,
    )
    return Expectation.phase_agnostic(
        symbol_usages=asrt.matches_sequence([
            asrt_sym_usage.matches_definition(asrt.equals(defined_name),
                                              expected_container),
        ]),
        symbols_after_main=assert_symbol_table_is_singleton(
            defined_name,
            expected_container,
        )
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
