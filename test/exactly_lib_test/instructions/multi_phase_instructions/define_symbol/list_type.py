import unittest

from exactly_lib.symbol.data import string_resolver as sr, list_resolver as lr
from exactly_lib.symbol.symbol_syntax import SymbolWithReferenceSyntax
from exactly_lib.symbol.symbol_usage import SymbolDefinition
from exactly_lib_test.instructions.multi_phase_instructions.define_symbol.test_case_base import TestCaseBaseForParser
from exactly_lib_test.instructions.multi_phase_instructions.define_symbol.test_resources import *
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.data.test_resources import references
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as vs_asrt
from exactly_lib_test.symbol.data.test_resources.data_symbol_utils import container
from exactly_lib_test.symbol.data.test_resources.symbol_structure_assertions import equals_container
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestListSuccessfulParse)


class TestListSuccessfulParse(TestCaseBaseForParser):
    def test_assignment_of_empty_list(self):
        symbol_name = 'the_symbol_name'
        source = single_line_source('{list_type} {symbol_name} = ',
                                    symbol_name=symbol_name)
        expected_resolver = lr.ListResolver([])
        expected_resolver_container = container(expected_resolver)
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(SymbolDefinition(symbol_name, expected_resolver_container),
                                      ignore_source_line=True)
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                symbol_name,
                equals_container(expected_resolver_container),
            )
        )
        self._check(source, ArrangementWithSds(), expectation)

    def test_assignment_of_list_with_multiple_constant_elements(self):
        symbol_name = 'the_symbol_name'
        value_without_space = 'value_without_space'
        value_with_space = 'value with space'
        source = remaining_source(src(
            '{list_type} {symbol_name} = {value_without_space} {soft_quote}{value_with_space}{soft_quote} ',
            symbol_name=symbol_name,
            value_without_space=value_without_space,
            value_with_space=value_with_space,
        ),
            ['following line'],
        )
        expected_resolver = lr.ListResolver([lr.StringResolverElement(sr.string_constant(value_without_space)),
                                             lr.StringResolverElement(sr.string_constant(value_with_space))])
        expected_resolver_container = container(expected_resolver)

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(SymbolDefinition(symbol_name, expected_resolver_container),
                                      ignore_source_line=True)
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                symbol_name,
                equals_container(expected_resolver_container),
            ),
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
        )
        self._check(source, ArrangementWithSds(), expectation)

    def test_assignment_of_list_with_symbol_references(self):
        symbol_name = 'the_symbol_name'
        referred_symbol = SymbolWithReferenceSyntax('referred_symbol')
        source = remaining_source(src(
            '{list_type} {symbol_name} = {symbol_reference} ',
            symbol_name=symbol_name,
            symbol_reference=referred_symbol,
        ),
            ['following line'],
        )
        expected_symbol_reference = references.reference_to_any_data_type_value(referred_symbol.name)
        expected_resolver = lr.ListResolver([lr.SymbolReferenceElement(expected_symbol_reference)])

        expected_resolver_container = container(expected_resolver)

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(SymbolDefinition(symbol_name, expected_resolver_container),
                                      ignore_source_line=True)
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                symbol_name,
                equals_container(expected_resolver_container),
            ),
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
        )
        self._check(source, ArrangementWithSds(), expectation)
