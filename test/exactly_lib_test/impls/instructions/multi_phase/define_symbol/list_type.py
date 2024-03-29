import unittest

from exactly_lib.type_val_deps.types.list_ import defs
from exactly_lib.type_val_deps.types.list_ import list_sdvs as sdvs
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.abstract_syntax import \
    DefineSymbolWOptionalValue
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.embryo_checker import \
    INSTRUCTION_CHECKER, PARSE_CHECKER
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.source_formatting import *
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import Arrangement, \
    MultiSourceExpectation
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import references
from exactly_lib_test.type_val_deps.types.list_.test_resources.abstract_syntax import ListAbsStx, \
    ListSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.list_.test_resources.abstract_syntaxes import EmptyListAbsStx, \
    NonEmptyListAbsStx, ListElementStringAbsStx
from exactly_lib_test.type_val_deps.types.list_.test_resources.symbol_context import ListSymbolContext
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import SOME_INVALID_STRINGS, \
    StringLiteralAbsStx
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(TestListSuccessfulParse),
    ])


class TestInvalidSyntax(unittest.TestCase):
    def test_invalid_string(self):
        for invalid_string in SOME_INVALID_STRINGS:
            invalid_list = NonEmptyListAbsStx([ListElementStringAbsStx(invalid_string)])
            PARSE_CHECKER.check_invalid_syntax__abs_stx(
                self,
                invalid_list,
                sub_test_identifiers={
                    'invalid_string': repr(invalid_string.value)
                }
            )

    def test_superfluous_arguments_after_explicit_list_delimiter(self):
        stop_element = ListElementStringAbsStx(StringLiteralAbsStx(defs.STOP_AT_CHAR))
        invalid_list = NonEmptyListAbsStx([
            stop_element,
            ListElementStringAbsStx(StringLiteralAbsStx('valid')),
        ])
        PARSE_CHECKER.check_invalid_syntax__abs_stx(
            self,
            invalid_list,
        )


class TestListSuccessfulParse(unittest.TestCase):
    def test_assignment_of_empty_list(self):
        list_symbol = ListSymbolContext.of_empty('the_symbol_name')

        syntax = _syntax(list_symbol, EmptyListAbsStx())

        expectation = MultiSourceExpectation.phase_agnostic(
            symbol_usages=asrt.matches_sequence([
                list_symbol.assert_matches_definition_of_sdv
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                list_symbol.name,
                list_symbol.value.assert_matches_container_of_sdv,
            ),
        )

        INSTRUCTION_CHECKER.check__abs_stx__layout_and_source_variants(
            self,
            syntax,
            Arrangement.phase_agnostic(),
            expectation,
        )

    def test_assignment_of_list_with_multiple_constant_elements(self):
        # ARRANGE #
        value_without_space = 'value_without_space'
        value_with_space = 'value with space'

        symbol_to_assign = ListSymbolContext.of_sdv(
            'the_symbol_name',
            sdvs.from_str_constants([value_without_space,
                                     value_with_space])
        )

        syntax = _syntax(symbol_to_assign,
                         NonEmptyListAbsStx([
                             ListElementStringAbsStx.of_str(value_without_space),
                             ListElementStringAbsStx.of_str(value_with_space, QuoteType.SOFT),
                         ]))

        expectation = MultiSourceExpectation.phase_agnostic(
            symbol_usages=asrt.matches_sequence([
                symbol_to_assign.assert_matches_definition_of_sdv
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                symbol_to_assign.name,
                symbol_to_assign.value.assert_matches_container_of_sdv,
            ),
        )
        # ACT & ASSERT #
        INSTRUCTION_CHECKER.check__abs_stx__layout_and_source_variants(
            self,
            syntax,
            Arrangement.phase_agnostic(),
            expectation,
        )

    def test_assignment_of_list_with_symbol_references(self):
        # ARRANGE #
        referred_symbol_name = 'referred_symbol'
        expected_symbol_reference = references.reference_to__w_str_rendering(referred_symbol_name)
        symbol_to_assign = ListSymbolContext.of_sdv(
            'the_symbol_name',
            sdvs.from_elements([sdvs.symbol_element(expected_symbol_reference)])
        )

        syntax = _syntax(symbol_to_assign, ListSymbolReferenceAbsStx(referred_symbol_name))
        # ACT & ASSERT #
        INSTRUCTION_CHECKER.check__abs_stx__layout_and_source_variants(
            self,
            syntax,
            Arrangement.phase_agnostic(),
            MultiSourceExpectation.phase_agnostic(
                symbol_usages=asrt.matches_sequence([
                    symbol_to_assign.assert_matches_definition_of_sdv
                ]),
                symbols_after_main=assert_symbol_table_is_singleton(
                    symbol_to_assign.name,
                    symbol_to_assign.value.assert_matches_container_of_sdv,
                ),
            ),
        )


def _syntax(symbol: ListSymbolContext, value: ListAbsStx) -> AbstractSyntax:
    return DefineSymbolWOptionalValue(symbol.name, ValueType.LIST, value)
