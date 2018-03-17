import unittest

from exactly_lib.instructions.multi_phase_instructions import define_symbol as sut
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_syntax import SymbolWithReferenceSyntax, symbol, constant
from exactly_lib.symbol.symbol_usage import SymbolDefinition
from exactly_lib_test.instructions.multi_phase_instructions.define_symbol.test_case_base import TestCaseBaseForParser
from exactly_lib_test.instructions.multi_phase_instructions.define_symbol.test_resources import *
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as vs_asrt
from exactly_lib_test.symbol.data.test_resources.data_symbol_utils import string_constant_container, \
    container
from exactly_lib_test.symbol.data.test_resources.symbol_structure_assertions import equals_container
from exactly_lib_test.test_case_utils.parse.parse_string import string_resolver_from_fragments
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseDueToInvalidSyntax),
        unittest.makeSuite(TestSuccessfulDefinition),
    ])


class TestFailingParseDueToInvalidSyntax(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('Missing end quote (soft)',
             src('{string_type} name = "string')
             ),
            ('Missing end quote (hard)',
             src('{string_type} name = \'string')
             ),
            ('Superfluous arguments',
             src('{path_type} name = x superfluous-arg')
             ),
        ]
        parser = sut.EmbryoParser()
        for (case_name, source_str) in test_cases:
            source = remaining_source(source_str)
            with self.subTest(msg=case_name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class TestSuccessfulDefinition(TestCaseBaseForParser):
    def test_assignment_of_single_constant_word(self):
        source = single_line_source('{string_type} name1 = v1')
        expected_definition = SymbolDefinition('name1', string_constant_container('v1'))
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(expected_definition, ignore_source_line=True)
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                'name1',
                equals_container(string_constant_container('v1')),
            )
        )
        self._check(source, ArrangementWithSds(), expectation)

    def test_assignment_of_single_symbol_reference(self):
        # ARRANGE #
        referred_symbol = SymbolWithReferenceSyntax('referred_symbol')
        name_of_defined_symbol = 'defined_symbol'
        source = single_line_source('{string_type} {name} = {symbol_reference}',
                                    name=name_of_defined_symbol,
                                    symbol_reference=referred_symbol)
        expected_resolver = string_resolver_from_fragments([symbol(referred_symbol.name)])
        container_of_expected_resolver = container(expected_resolver)
        expected_definition = SymbolDefinition(name_of_defined_symbol,
                                               container_of_expected_resolver)
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(expected_definition, ignore_source_line=True),
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                name_of_defined_symbol,
                equals_container(container_of_expected_resolver),
            )
        )
        # ACT & ASSERT #
        self._check(source, ArrangementWithSds(), expectation)

    def test_assignment_of_single_symbol_reference_syntax_within_hard_quotes(self):
        # ARRANGE #
        referred_symbol = SymbolWithReferenceSyntax('referred_symbol')
        name_of_defined_symbol = 'defined_symbol'
        source = single_line_source('{string_type} {name} = {hard_quote}{symbol_reference}{hard_quote}',
                                    name=name_of_defined_symbol,
                                    hard_quote=HARD_QUOTE_CHAR,
                                    symbol_reference=referred_symbol)
        expected_resolver = string_resolver_from_fragments([constant(str(referred_symbol))])
        container_of_expected_resolver = container(expected_resolver)
        expected_definition = SymbolDefinition(name_of_defined_symbol,
                                               container_of_expected_resolver)
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(expected_definition, ignore_source_line=True),
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                name_of_defined_symbol,
                equals_container(container_of_expected_resolver),
            )
        )
        # ACT & ASSERT #
        self._check(source, ArrangementWithSds(), expectation)

    def test_assignment_of_symbols_and_constant_text_within_soft_quotes(self):
        # ARRANGE #
        referred_symbol1 = SymbolWithReferenceSyntax('referred_symbol_1')
        referred_symbol2 = SymbolWithReferenceSyntax('referred_symbol_2')
        name_of_defined_symbol = 'defined_symbol'
        source = single_line_source('{string_type} {name} = {soft_quote}{sym_ref1} between {sym_ref2}{soft_quote}',
                                    soft_quote=SOFT_QUOTE_CHAR,
                                    name=name_of_defined_symbol,
                                    sym_ref1=referred_symbol1,
                                    sym_ref2=referred_symbol2)
        expected_resolver = string_resolver_from_fragments([
            symbol(referred_symbol1.name),
            constant(' between '),
            symbol(referred_symbol2.name),
        ])
        container_of_expected_resolver = container(expected_resolver)
        expected_definition = SymbolDefinition(name_of_defined_symbol,
                                               container_of_expected_resolver)
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(expected_definition, ignore_source_line=True),
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                name_of_defined_symbol,
                equals_container(container_of_expected_resolver),
            )
        )
        # ACT & ASSERT #
        self._check(source, ArrangementWithSds(), expectation)
