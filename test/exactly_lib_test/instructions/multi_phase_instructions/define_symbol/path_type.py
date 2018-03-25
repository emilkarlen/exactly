import unittest

from exactly_lib.help_texts.file_ref import REL_ACT_OPTION
from exactly_lib.instructions.multi_phase_instructions import define_symbol as sut
from exactly_lib.instructions.multi_phase_instructions.define_symbol import REL_OPTIONS_CONFIGURATION
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.data.file_ref_resolver_impls.file_ref_resolvers import FileRefConstant
from exactly_lib.symbol.data.file_ref_resolver_impls.file_ref_with_symbol import rel_symbol
from exactly_lib.symbol.data.file_ref_resolver_impls.path_part_resolvers import PathPartResolverAsFixedPath
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import FileRefRelativityRestriction
from exactly_lib.symbol.symbol_usage import SymbolDefinition, SymbolReference
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib_test.instructions.multi_phase_instructions.define_symbol.test_case_base import TestCaseBaseForParser
from exactly_lib_test.instructions.multi_phase_instructions.define_symbol.test_resources import *
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as vs_asrt
from exactly_lib_test.symbol.data.test_resources.symbol_structure_assertions import equals_container
from exactly_lib_test.symbol.data.test_resources.symbol_usage_assertions import \
    assert_symbol_usages_is_singleton_list
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseDueToInvalidSyntax),
        unittest.makeSuite(TestAssignmentRelativeSingleValidOption),
        unittest.makeSuite(TestAssignmentRelativeSingleDefaultOption),
        unittest.makeSuite(TestAssignmentRelativeSymbolDefinition),
    ])


class TestFailingParseDueToInvalidSyntax(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('Invalid file ref syntax',
             src('{path_type} name = --invalid-option x')
             ),
            ('Superfluous arguments',
             src('{path_type} name = {rel_opt} x superfluous-arg',
                 rel_opt=REL_ACT_OPTION)
             ),
        ]
        parser = sut.EmbryoParser()
        for (case_name, source_str) in test_cases:
            source = remaining_source(source_str)
            with self.subTest(msg=case_name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class TestAssignmentRelativeSingleValidOption(TestCaseBaseForParser):
    def test(self):
        instruction_argument = src('{path_type} name = --rel-act component')
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_resolver = FileRefConstant(file_refs.rel_act(PathPartAsFixedPath('component')))
            expected_container = resolver_container(expected_file_ref_resolver)
            self._check(source,
                        ArrangementWithSds(),
                        Expectation(
                            symbol_usages=assert_symbol_usages_is_singleton_list(
                                vs_asrt.equals_symbol(
                                    SymbolDefinition('name', expected_container))),
                            symbols_after_main=assert_symbol_table_is_singleton(
                                'name',
                                equals_container(expected_container))
                        )
                        )


class TestAssignmentRelativeSingleDefaultOption(TestCaseBaseForParser):
    def test(self):
        instruction_argument = src('{path_type} name = component')
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_resolver = FileRefConstant(
                file_refs.of_rel_option(REL_OPTIONS_CONFIGURATION.default_option,
                                        PathPartAsFixedPath('component')))
            expected_container = resolver_container(expected_file_ref_resolver)
            self._check(source,
                        ArrangementWithSds(),
                        Expectation(
                            symbol_usages=assert_symbol_usages_is_singleton_list(
                                vs_asrt.equals_symbol(
                                    SymbolDefinition('name', expected_container))),
                            symbols_after_main=assert_symbol_table_is_singleton(
                                'name',
                                equals_container(expected_container)))
                        )


class TestAssignmentRelativeSymbolDefinition(TestCaseBaseForParser):
    def test(self):
        instruction_argument = src('{path_type} ASSIGNED_NAME = --rel REFERENCED_SYMBOL component')
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_resolver = rel_symbol(
                SymbolReference('REFERENCED_SYMBOL',
                                ReferenceRestrictionsOnDirectAndIndirect(FileRefRelativityRestriction(
                                    REL_OPTIONS_CONFIGURATION.accepted_relativity_variants))),
                PathPartResolverAsFixedPath('component'))
            expected_container = resolver_container(expected_file_ref_resolver)
            self._check(source,
                        ArrangementWithSds(),
                        Expectation(
                            symbol_usages=asrt.matches_sequence([
                                vs_asrt.equals_symbol(
                                    SymbolDefinition('ASSIGNED_NAME',
                                                     expected_container),
                                    ignore_source_line=True)
                            ]),
                            symbols_after_main=assert_symbol_table_is_singleton(
                                'ASSIGNED_NAME',
                                equals_container(expected_container)))
                        )
