import unittest

from exactly_lib.instructions.multi_phase.define_symbol import parser as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_syntax import SymbolWithReferenceSyntax, symbol, constant
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources.embryo_checker import INSTRUCTION_CHECKER
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources.source_formatting import *
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_utils.parse.parse_string import string_sdv_from_fragments
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string.test_resources.here_doc_assertion_utils import here_doc_lines
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext, \
    StringSymbolContext
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseDueToInvalidSyntax),
        unittest.makeSuite(TestSuccessfulDefinition),
        unittest.makeSuite(TestSuccessfulDefinitionFromHereDocument),
    ])


class TestFailingParseDueToInvalidSyntax(unittest.TestCase):
    def runTest(self):
        test_cases = [
            NameAndValue(
                'Missing end quote (soft)',
                src2(ValueType.STRING, 'name', '{soft_quote}string')
            ),
            NameAndValue(
                'Missing end quote (hard)',
                src2(ValueType.STRING, 'name', '{hard_quote}string')
            ),
            NameAndValue(
                'Superfluous arguments',
                src2(ValueType.PATH, 'name', 'x superfluous-arg')
            ),
        ]
        parser = sut.EmbryoParser()
        for case in test_cases:
            source = remaining_source(case.value)
            with self.subTest(case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestSuccessfulDefinition(unittest.TestCase):
    def test_assignment_of_single_constant_word(self):
        argument_cases = [
            NameAndValue('value on same line',
                         '{string_type} name1 = v1'
                         ),
            NameAndValue('value on following line',
                         '{string_type} name1 = {new_line} v1'
                         ),
        ]

        for argument_case in argument_cases:
            with self.subTest(argument_case.name):
                source = arbitrary_string_source(argument_case.value)
                expected_symbol = StringConstantSymbolContext('name1', 'v1')
                expectation = Expectation(
                    symbol_usages=asrt.matches_sequence([
                        expected_symbol.assert_matches_definition_of_sdv
                    ]),
                    symbols_after_main=assert_symbol_table_is_singleton(
                        'name1',
                        expected_symbol.value.assert_matches_container_of_sdv,
                    )
                )
                INSTRUCTION_CHECKER.check(self, source, ArrangementWithSds(), expectation)

    def test_assignment_of_single_symbol_reference(self):
        # ARRANGE #
        referred_symbol = SymbolWithReferenceSyntax('referred_symbol')
        assigned_symbol = StringSymbolContext.of_sdv('defined_symbol',
                                                     string_sdv_from_fragments([symbol(referred_symbol.name)]))
        source = single_line_source('{string_type} {name} = {symbol_reference}',
                                    name=assigned_symbol.name,
                                    symbol_reference=referred_symbol)
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                assigned_symbol.assert_matches_definition_of_sdv,
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                assigned_symbol.name,
                assigned_symbol.value.assert_matches_container_of_sdv,
            )
        )
        # ACT & ASSERT #
        INSTRUCTION_CHECKER.check(self, source, ArrangementWithSds(), expectation)

    def test_assignment_of_single_symbol_reference_syntax_within_hard_quotes(self):
        # ARRANGE #
        referred_symbol = SymbolWithReferenceSyntax('referred_symbol')
        assigned_symbol = StringSymbolContext.of_sdv('defined_symbol',
                                                     string_sdv_from_fragments([constant(str(referred_symbol))]))
        source = single_line_source('{string_type} {name} = {hard_quote}{symbol_reference}{hard_quote}',
                                    name=assigned_symbol.name,
                                    hard_quote=HARD_QUOTE_CHAR,
                                    symbol_reference=referred_symbol)
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                assigned_symbol.assert_matches_definition_of_sdv,
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                assigned_symbol.name,
                assigned_symbol.value.assert_matches_container_of_sdv,
            )
        )
        # ACT & ASSERT #
        INSTRUCTION_CHECKER.check(self, source, ArrangementWithSds(), expectation)

    def test_assignment_of_symbols_and_constant_text_within_soft_quotes(self):
        # ARRANGE #
        referred_symbol1 = SymbolWithReferenceSyntax('referred_symbol_1')
        referred_symbol2 = SymbolWithReferenceSyntax('referred_symbol_2')
        assigned_symbol = StringSymbolContext.of_sdv(
            'defined_symbol',
            string_sdv_from_fragments([
                symbol(referred_symbol1.name),
                constant(' between '),
                symbol(referred_symbol2.name),
            ]))
        source = single_line_source('{string_type} {name} = {soft_quote}{sym_ref1} between {sym_ref2}{soft_quote}',
                                    soft_quote=SOFT_QUOTE_CHAR,
                                    name=assigned_symbol.name,
                                    sym_ref1=referred_symbol1,
                                    sym_ref2=referred_symbol2)
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                assigned_symbol.assert_matches_definition_of_sdv,
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                assigned_symbol.name,
                assigned_symbol.value.assert_matches_container_of_sdv,
            )
        )
        # ACT & ASSERT #
        INSTRUCTION_CHECKER.check(self, source, ArrangementWithSds(), expectation)


class TestSuccessfulDefinitionFromHereDocument(unittest.TestCase):
    def test_assignment_of_single_constant_line(self):
        value_str = 'value'
        symbol_name = 'name1'
        sb = SB.new_with(value_str=value_str,
                         symbol_name=symbol_name)

        source = sb.lines(
            here_doc_lines(first_line_start='{string_type} {symbol_name} = ',
                           marker='EOF',
                           contents_lines=['{value_str}']) +
            ['following line']
        )
        # EXPECTATION #
        expected_symbol = StringConstantSymbolContext(symbol_name, value_str + '\n')
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                expected_symbol.assert_matches_definition_of_sdv
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                symbol_name,
                expected_symbol.value.assert_matches_container_of_sdv,
            ),
            source=asrt_source.is_at_beginning_of_line(4)
        )
        # ACT & ASSERT #
        INSTRUCTION_CHECKER.check(self, source, ArrangementWithSds(), expectation)

    def test_assignment_of_single_symbol_reference(self):
        # ARRANGE #
        referred_symbol = SymbolWithReferenceSyntax('referred_symbol')
        expected_sdv = string_sdv_from_fragments([symbol(referred_symbol.name),
                                                  constant('\n')])
        assigned_symbol = StringSymbolContext.of_sdv(
            'defined_symbol',
            expected_sdv,
        )
        sb = SB.new_with(referred_symbol=referred_symbol,
                         name_of_defined_symbol=assigned_symbol.name)

        source = sb.lines(
            here_doc_lines(first_line_start='{string_type} {name_of_defined_symbol} = ',
                           marker='EOF',
                           contents_lines=[str(referred_symbol)])
        )
        # EXPECTATION #
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                assigned_symbol.assert_matches_definition_of_sdv,
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                assigned_symbol.name,
                assigned_symbol.value.assert_matches_container_of_sdv,
            )
        )
        # ACT & ASSERT #
        INSTRUCTION_CHECKER.check(self, source, ArrangementWithSds(), expectation)
