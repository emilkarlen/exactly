import unittest

from exactly_lib.definitions.path import REL_ACT_OPTION
from exactly_lib.impls.instructions.multi_phase.define_symbol import parser as sut
from exactly_lib.impls.instructions.multi_phase.define_symbol import type_parser
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.source_location import FileLocationInfo, FileSystemLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import PathRelativityRestriction
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.path import path_part_sdvs
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.embryo_checker import \
    INSTRUCTION_CHECKER
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.source_formatting import *
from exactly_lib_test.impls.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.path.test_resources.path import PathSymbolValueContext, \
    ConstantSuffixPathDdvSymbolContext, \
    PathSymbolContext
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
            NameAndValue('Invalid path syntax',
                         src2(ValueType.PATH, 'name', '{invalid_option} x',
                              invalid_option=option_syntax.long_option_syntax('invalid-option'))
                         ),
            NameAndValue('Superfluous arguments',
                         src2(ValueType.PATH, 'name', '{rel_opt} x superfluous-arg',
                              rel_opt=REL_ACT_OPTION)
                         ),
            NameAndValue('Missing PATH',
                         src2(ValueType.PATH, 'name', '')
                         ),
        ]
        parser = sut.EmbryoParser()
        for case in test_cases:
            source = remaining_source(case.value)
            with self.subTest(msg=case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestAssignmentRelativeSingleValidOption(unittest.TestCase):
    def test(self):

        expected_defined_symbol = ConstantSuffixPathDdvSymbolContext('name',
                                                                     RelOptionType.REL_ACT,
                                                                     'component')
        argument_cases = [
            NameAndValue('value on same line',
                         '{rel_act} {suffix}'
                         ),
            NameAndValue('value on following line',
                         '{new_line} {rel_act} {suffix}'
                         ),
        ]

        for argument_case in argument_cases:
            with self.subTest(arguments=argument_case.name):
                instruction_argument = src2(ValueType.PATH,
                                            expected_defined_symbol.name,
                                            argument_case.value,
                                            suffix=expected_defined_symbol.path_suffix)
                for source in equivalent_source_variants__with_source_check__consume_last_line(self,
                                                                                               instruction_argument):
                    INSTRUCTION_CHECKER.check(self,
                                              source,
                                              ArrangementWithSds(),
                                              Expectation(
                                                  symbol_usages=asrt.matches_singleton_sequence(
                                                      expected_defined_symbol.assert_matches_definition_of_sdv
                                                  ),
                                                  symbols_after_main=assert_symbol_table_is_singleton(
                                                      expected_defined_symbol.name,
                                                      expected_defined_symbol.value.assert_matches_container_of_sdv)
                                              )
                                              )


class TestAssignmentRelativeSingleDefaultOption(unittest.TestCase):
    def test(self):
        expected_defined_symbol = ConstantSuffixPathDdvSymbolContext(
            'name',
            type_parser.REL_OPTIONS_CONFIGURATION.default_option,
            'component')

        instruction_argument = src2(ValueType.PATH,
                                    expected_defined_symbol.name,
                                    expected_defined_symbol.path_suffix)

        for source in equivalent_source_variants__with_source_check__consume_last_line(self, instruction_argument):
            INSTRUCTION_CHECKER.check(
                self,
                source,
                ArrangementWithSds(),
                Expectation(
                    symbol_usages=asrt.matches_singleton_sequence(
                        expected_defined_symbol.assert_matches_definition_of_sdv
                    ),
                    symbols_after_main=assert_symbol_table_is_singleton(
                        'name',
                        expected_defined_symbol.value.assert_matches_container_of_sdv))
            )


class TestAssignmentRelativeSymbolDefinition(unittest.TestCase):
    def test(self):
        instruction_argument = src2(ValueType.PATH, 'ASSIGNED_NAME', '{rel_symbol} REFERENCED_SYMBOL component')
        for source in equivalent_source_variants__with_source_check__consume_last_line(self, instruction_argument):
            expected_path_sdv = path_sdvs.rel_symbol(
                SymbolReference('REFERENCED_SYMBOL',
                                ReferenceRestrictionsOnDirectAndIndirect(PathRelativityRestriction(
                                    type_parser.REL_OPTIONS_CONFIGURATION.accepted_relativity_variants))),
                path_part_sdvs.from_constant_str('component'))
            expected_symbol_value = PathSymbolValueContext.of_sdv(expected_path_sdv)
            expected_symbol = PathSymbolContext('ASSIGNED_NAME', expected_symbol_value)
            INSTRUCTION_CHECKER.check(
                self,
                source,
                ArrangementWithSds(),
                Expectation(
                    symbol_usages=asrt.matches_sequence([
                        expected_symbol.assert_matches_definition_of_sdv
                    ]),
                    symbols_after_main=assert_symbol_table_is_singleton(
                        expected_symbol.name,
                        expected_symbol_value.assert_matches_container_of_sdv))
            )


class TestAssignmentRelativeSourceFileLocation(unittest.TestCase):
    def test(self):
        with tmp_dir() as abs_path_of_dir_containing_last_file_base_name:
            fs_location_info = FileSystemLocationInfo(
                FileLocationInfo(abs_path_of_dir_containing_last_file_base_name))
            instruction_argument = src2(ValueType.PATH, 'name', '{rel_source_file} component')
            for source in equivalent_source_variants__with_source_check__consume_last_line(self, instruction_argument):
                expected_path_sdv = path_sdvs.constant(
                    path_ddvs.rel_abs_path(abs_path_of_dir_containing_last_file_base_name,
                                           path_ddvs.constant_path_part('component')))
                expected_symbol_value = PathSymbolValueContext.of_sdv(expected_path_sdv)
                expected_symbol = PathSymbolContext('name', expected_symbol_value)
                INSTRUCTION_CHECKER.check(
                    self,
                    source,
                    ArrangementWithSds(fs_location_info=fs_location_info),
                    Expectation(
                        symbol_usages=asrt.matches_singleton_sequence(
                            expected_symbol.assert_matches_definition_of_sdv
                        ),
                        symbols_after_main=assert_symbol_table_is_singleton(
                            'name',
                            expected_symbol_value.assert_matches_container_of_sdv)
                    )
                )
