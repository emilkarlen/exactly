import unittest

from exactly_lib.symbol.symbol_syntax import SymbolWithReferenceSyntax
from exactly_lib.type_val_deps.types.list_ import list_sdvs as lrs
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.embryo_checker import \
    INSTRUCTION_CHECKER
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.source_formatting import *
from exactly_lib_test.impls.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.impls.types.parse.test_resources.source_case import SourceCase
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.data.test_resources import references
from exactly_lib_test.type_val_deps.types.list_.test_resources.list_ import ListSymbolContext
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestListSuccessfulParse)


class TestListSuccessfulParse(unittest.TestCase):
    def test_assignment_of_empty_list(self):
        list_symbol = ListSymbolContext.of_empty('the_symbol_name')
        sb = SB.new_with(symbol_name=list_symbol.name)

        cases = [
            SourceCase('No following lines',
                       source=sb.single_line('{list_type} {symbol_name} = '),
                       source_assertion=asrt_source.source_is_at_end
                       ),
            SourceCase('Following lines',
                       source=sb.lines(['{list_type} {symbol_name} = ',
                                        'following line'],
                                       ),
                       source_assertion=asrt_source.is_at_beginning_of_line(2)
                       ),
        ]

        for case in cases:
            with self.subTest(case.name):
                expectation = Expectation(
                    symbol_usages=asrt.matches_sequence([
                        list_symbol.assert_matches_definition_of_sdv
                    ]),
                    symbols_after_main=assert_symbol_table_is_singleton(
                        list_symbol.name,
                        list_symbol.value.assert_matches_container_of_sdv,
                    ),
                    source=case.source_assertion
                )
                INSTRUCTION_CHECKER.check(self, case.source, ArrangementWithSds(), expectation)

    def test_assignment_of_list_with_multiple_constant_elements(self):
        value_without_space = 'value_without_space'
        value_with_space = 'value with space'
        symbol_to_assign = ListSymbolContext.of_sdv(
            'the_symbol_name',
            lrs.from_str_constants([value_without_space,
                                    value_with_space])
        )

        sb = SB.new_with(symbol_name=symbol_to_assign.name,
                         value_without_space=value_without_space,
                         value_with_space=value_with_space)
        cases = [
            SourceCase('No following lines',
                       source=sb.single_line(
                           '{list_type} {symbol_name} = '
                           '{value_without_space} {soft_quote}{value_with_space}{soft_quote} '),
                       source_assertion=asrt_source.source_is_at_end
                       ),
            SourceCase('Following lines',
                       source=sb.lines(
                           [
                               '{list_type} {symbol_name} = '
                               '{value_without_space} {soft_quote}{value_with_space}{soft_quote}',
                               'following line',
                           ]),
                       source_assertion=asrt_source.is_at_beginning_of_line(2)
                       ),
        ]

        for case in cases:
            with self.subTest(case.name):
                expectation = Expectation(
                    symbol_usages=asrt.matches_sequence([
                        symbol_to_assign.assert_matches_definition_of_sdv
                    ]),
                    symbols_after_main=assert_symbol_table_is_singleton(
                        symbol_to_assign.name,
                        symbol_to_assign.value.assert_matches_container_of_sdv,
                    ),
                    source=case.source_assertion,
                )
                INSTRUCTION_CHECKER.check(self, case.source, ArrangementWithSds(), expectation)

    def test_assignment_of_list_with_symbol_references(self):
        referred_symbol = SymbolWithReferenceSyntax('referred_symbol')
        expected_symbol_reference = references.reference_to_any_data_type_value(referred_symbol.name)
        symbol_to_assign = ListSymbolContext.of_sdv(
            'the_symbol_name',
            lrs.from_elements([lrs.symbol_element(expected_symbol_reference)])
        )

        source = remaining_source(
            src2(ValueType.LIST, symbol_to_assign.name, str(referred_symbol)),
            ['following line'],
        )

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                symbol_to_assign.assert_matches_definition_of_sdv
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                symbol_to_assign.name,
                symbol_to_assign.value.assert_matches_container_of_sdv,
            ),
            source=asrt_source.is_at_beginning_of_line(2),
        )
        INSTRUCTION_CHECKER.check(self, source, ArrangementWithSds(), expectation)
