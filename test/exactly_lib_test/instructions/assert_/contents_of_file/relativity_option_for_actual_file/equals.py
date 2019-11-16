import unittest

from exactly_lib.symbol.data import path_resolvers
from exactly_lib.symbol.data.restrictions.value_restrictions import PathRelativityRestriction
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import parse_here_doc_or_path
from exactly_lib.type_system.data import paths
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib_test.instructions.assert_.contents_of_file.relativity_option_for_actual_file.test_resources import \
    RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE
from exactly_lib_test.instructions.assert_.contents_of_file.test_resources.test_base_classes import \
    TestWithConfigurationAndRelativityOptionAndNegationForConstArgsBase
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    suite_for__conf__rel_opts__negations
from exactly_lib_test.instructions.assert_.test_resources.file_contents.util.expectation_utils import \
    expectation_that_file_for_actual_contents_is_invalid
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    equals_path_relativity_restriction
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import \
    equals_symbol_reference_with_restriction_on_direct_target
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources import tcds_populators
from exactly_lib_test.test_case_file_structure.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.misc import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir, File, empty_file
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources import symbol_tables


def suite_for(instruction_configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return suite_for__conf__rel_opts__negations(instruction_configuration,
                                                RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE,
                                                [
                                                    _ErrorWhenActualFileDoesNotExist,
                                                    _ErrorWhenActualFileIsADirectory,
                                                    _ContentsDiffer,
                                                    _ContentsEquals,
                                                    _ContentsEqualsWithExpectedFileRelHdsSymbol,
                                                    _ContentsEqualsWithExpectedFileRelTmpSymbol,
                                                ]
                                                )


class _ErrorWhenActualFileDoesNotExist(TestWithConfigurationAndRelativityOptionAndNegationForConstArgsBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {maybe_not} {equals} '
                 '{file_option} {rel_hds_case_option} expected.txt',
                 relativity_option=self.rel_opt.option_argument,
                 maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative),
            ArrangementPostAct(
                hds_contents=hds_case_dir_contents(
                    DirContents([empty_file('expected.txt')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            expectation_that_file_for_actual_contents_is_invalid(self.rel_opt),
        )


class _ErrorWhenActualFileIsADirectory(TestWithConfigurationAndRelativityOptionAndNegationForConstArgsBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            args(
                '{relativity_option} actual-dir {maybe_not} {equals} {file_option} {rel_hds_case_option} expected.txt',
                relativity_option=self.rel_opt.option_argument,
                maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative),
            ArrangementPostAct(
                hds_contents=hds_case_dir_contents(
                    DirContents([File('expected.txt', 'expected contents')])),
                tcds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([empty_dir('actual-dir')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            expectation_that_file_for_actual_contents_is_invalid(self.rel_opt),
        )


class _ContentsDiffer(TestWithConfigurationAndRelativityOptionAndNegationForConstArgsBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            args(
                '{relativity_option} actual.txt {maybe_not} {equals} {file_option} {rel_hds_case_option} expected.txt',
                relativity_option=self.rel_opt.option_argument,
                maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative),
            ArrangementPostAct(
                hds_contents=hds_case_dir_contents(
                    DirContents([File('expected.txt', 'expected contents')])),
                tcds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', 'not equal to expected contents')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.fail__if_positive__pass_if_negative,
                symbol_usages=self.rel_opt.symbols.usages_expectation(),
            ),
        )


class _ContentsEquals(TestWithConfigurationAndRelativityOptionAndNegationForConstArgsBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            args(
                '{relativity_option} actual.txt {maybe_not} {equals} {file_option} {rel_hds_case_option} expected.txt',
                relativity_option=self.rel_opt.option_argument,
                maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative),
            ArrangementPostAct(
                hds_contents=hds_case_dir_contents(
                    DirContents([File('expected.txt', 'expected contents')])),
                tcds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', 'expected contents')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.pass__if_positive__fail__if_negative,
                symbol_usages=self.rel_opt.symbols.usages_expectation(),
            ),
        )


class _ContentsEqualsWithExpectedRelSymbolBase(TestWithConfigurationAndRelativityOptionAndNegationForConstArgsBase):
    def relativity_of_expected_file(self) -> RelOptionType:
        raise NotImplementedError()

    def runTest(self):
        from exactly_lib.test_case_utils.string_matcher.parse.parts.equality import \
            EXPECTED_FILE_REL_OPT_ARG_CONFIG

        expected_file_relativity_symbol = 'EXPECTED_RELATIVITY_SYMBOL_NAME'
        path_sym_tbl_entry_for_expected_file = data_symbol_utils.entry(
            expected_file_relativity_symbol,
            path_resolvers.constant(paths.of_rel_option(self.relativity_of_expected_file(),
                                                        paths.empty_path_part())))

        symbols_in_arrangement = symbol_tables.symbol_table_from_entries(
            [path_sym_tbl_entry_for_expected_file] +
            self.rel_opt.symbols.entries_for_arrangement())

        symbol_usage_expectation_for_expected_file = equals_symbol_reference_with_restriction_on_direct_target(
            expected_file_relativity_symbol,
            equals_path_relativity_restriction(
                PathRelativityRestriction(
                    EXPECTED_FILE_REL_OPT_ARG_CONFIG.options.accepted_relativity_variants)))

        expected_symbol_usages = asrt.matches_sequence(
            self.rel_opt.symbols.usage_expectation_assertions() +
            [symbol_usage_expectation_for_expected_file])

        populator_of_expected_files = tcds_populators.TcdsPopulatorForRelOptionType(
            self.relativity_of_expected_file(),
            DirContents([File('expected.txt', 'expected contents')]))
        populator_of_actual_files = self.rel_opt.populator_for_relativity_option_root(
            DirContents([File('actual.txt', 'expected contents')]))
        home_or_sds_contents_arrangement = tcds_populators.multiple([
            populator_of_actual_files,
            populator_of_expected_files
        ])
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {maybe_not} {equals} '
                 '{file_option} {rel_symbol_option} {rel_symbol_name} expected.txt',
                 relativity_option=self.rel_opt.option_argument,
                 maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                 file_option=option_syntax(parse_here_doc_or_path.FILE_ARGUMENT_OPTION),
                 rel_symbol_name=expected_file_relativity_symbol),
            ArrangementPostAct(
                tcds_contents=home_or_sds_contents_arrangement,
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbols_in_arrangement,
            ),
            Expectation(
                main_result=self.not_opt.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_usages,
            ),
        )


class _ContentsEqualsWithExpectedFileRelHdsSymbol(_ContentsEqualsWithExpectedRelSymbolBase):
    def relativity_of_expected_file(self) -> RelOptionType:
        return RelOptionType.REL_HDS_CASE


class _ContentsEqualsWithExpectedFileRelTmpSymbol(_ContentsEqualsWithExpectedRelSymbolBase):
    def relativity_of_expected_file(self) -> RelOptionType:
        return RelOptionType.REL_TMP
