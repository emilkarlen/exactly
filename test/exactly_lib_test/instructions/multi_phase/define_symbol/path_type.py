import unittest

from exactly_lib.definitions.file_ref import REL_ACT_OPTION
from exactly_lib.instructions.multi_phase import define_symbol as sut
from exactly_lib.instructions.multi_phase.define_symbol import REL_OPTIONS_CONFIGURATION
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_section import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parsing_configuration import FileSystemLocationInfo, SourceLocationInfo
from exactly_lib.symbol.data import file_ref_resolvers, path_part_resolvers
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.data.restrictions.value_restrictions import FileRefRelativityRestriction
from exactly_lib.symbol.symbol_usage import SymbolDefinition, SymbolReference
from exactly_lib.type_system.data import file_refs
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib_test.instructions.multi_phase.define_symbol.test_case_base import TestCaseBaseForParser
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources import *
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as vs_asrt
from exactly_lib_test.symbol.data.test_resources.symbol_structure_assertions import equals_container
from exactly_lib_test.symbol.data.test_resources.symbol_usage_assertions import \
    assert_symbol_usages_is_singleton_list
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseDueToInvalidSyntax),
        unittest.makeSuite(TestAssignmentRelativeSingleValidOption),
        unittest.makeSuite(TestAssignmentRelativeSingleDefaultOption),
        unittest.makeSuite(TestAssignmentRelativeSymbolDefinition),
        unittest.makeSuite(TestAssignmentRelativeSourceFileLocation),
    ])


class TestFailingParseDueToInvalidSyntax(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('Invalid file ref syntax',
             src('{path_type} name = {invalid_option} x',
                 invalid_option=option_syntax.long_option_syntax('invalid-option'))
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
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestAssignmentRelativeSingleValidOption(TestCaseBaseForParser):
    def test(self):
        instruction_argument = src('{path_type} name = {rel_act} component')
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_resolver = file_ref_resolvers.constant(
                file_refs.rel_act(file_refs.constant_path_part('component')))
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
            expected_file_ref_resolver = file_ref_resolvers.constant(
                file_refs.of_rel_option(REL_OPTIONS_CONFIGURATION.default_option,
                                        file_refs.constant_path_part('component')))
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
        instruction_argument = src('{path_type} ASSIGNED_NAME = {rel_symbol} REFERENCED_SYMBOL component')
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_resolver = file_ref_resolvers.rel_symbol(
                SymbolReference('REFERENCED_SYMBOL',
                                ReferenceRestrictionsOnDirectAndIndirect(FileRefRelativityRestriction(
                                    REL_OPTIONS_CONFIGURATION.accepted_relativity_variants))),
                path_part_resolvers.from_constant_str('component'))
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


class TestAssignmentRelativeSourceFileLocation(TestCaseBaseForParser):
    def test(self):
        with tmp_dir() as abs_path_of_dir_containing_file:
            fs_location_info = FileSystemLocationInfo(
                SourceLocationInfo(
                    abs_path_of_dir_containing_file=abs_path_of_dir_containing_file))
            instruction_argument = src('{path_type} name = {rel_source_file} component')
            for source in equivalent_source_variants__with_source_check(self, instruction_argument):
                expected_file_ref_resolver = file_ref_resolvers.constant(
                    file_refs.rel_abs_path(abs_path_of_dir_containing_file,
                                           file_refs.constant_path_part('component')))
                expected_container = resolver_container(expected_file_ref_resolver)
                self._check(source,
                            ArrangementWithSds(fs_location_info=fs_location_info),
                            Expectation(
                                symbol_usages=assert_symbol_usages_is_singleton_list(
                                    vs_asrt.equals_symbol(
                                        SymbolDefinition('name', expected_container))),
                                symbols_after_main=assert_symbol_table_is_singleton(
                                    'name',
                                    equals_container(expected_container))
                            )
                            )
