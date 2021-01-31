import unittest

from exactly_lib.impls.types.string_or_path import parse_string_or_path
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import PathRelativityRestriction
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib_test.impls.instructions.assert_.contents_of_file.relativity_option_for_actual_file.test_resources import \
    RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE
from exactly_lib_test.impls.instructions.assert_.contents_of_file.test_resources.test_base_classes import \
    TestWithConfigurationAndRelativityOptionAndNegationForConstArgsBase
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfiguration
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.relativity_options import \
    suite_for__conf__rel_opts__negations
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.util.expectation_utils import \
    expectation_that_file_for_actual_contents_is_invalid
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.types.string_matcher.test_resources.arguments_building import args
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import tcds_populators
from exactly_lib_test.tcfs.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.tcfs.test_resources.sub_dir_of_sds_act import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.data.test_resources.concrete_restriction_assertion import \
    equals_path_relativity_restriction
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    matches_symbol_reference_with_restriction_on_direct_target
from exactly_lib_test.type_val_deps.types.path.test_resources.path import PathDdvSymbolContext


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
                    DirContents([File.empty('expected.txt')])),
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
                    DirContents([Dir.empty('actual-dir')])),
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
        from exactly_lib.impls.types.string_matcher.parse.equality import \
            REL_OPT_CONFIG

        expected_file_relativity_symbol = 'EXPECTED_RELATIVITY_SYMBOL_NAME'
        path_symbol = PathDdvSymbolContext.of_no_suffix(
            expected_file_relativity_symbol,
            self.relativity_of_expected_file())

        symbols_in_arrangement = SymbolContext.symbol_table_of_contexts(
            [path_symbol] +
            self.rel_opt.symbols.contexts_for_arrangement())

        symbol_usage_expectation_for_expected_file = matches_symbol_reference_with_restriction_on_direct_target(
            expected_file_relativity_symbol,
            equals_path_relativity_restriction(
                PathRelativityRestriction(
                    REL_OPT_CONFIG.accepted_relativity_variants)))

        expected_symbol_usages = asrt.matches_sequence(
            self.rel_opt.symbols.usage_expectation_assertions() +
            [symbol_usage_expectation_for_expected_file])

        populator_of_expected_files = tcds_populators.TcdsPopulatorForRelOptionType(
            self.relativity_of_expected_file(),
            DirContents([File('expected.txt', 'expected contents')]))
        populator_of_actual_files = self.rel_opt.populator_for_relativity_option_root(
            DirContents([File('actual.txt', 'expected contents')]))
        tcds_contents_arrangement = tcds_populators.multiple([
            populator_of_actual_files,
            populator_of_expected_files
        ])
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {maybe_not} {equals} '
                 '{file_option} {rel_symbol_option} {rel_symbol_name} expected.txt',
                 relativity_option=self.rel_opt.option_argument,
                 maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                 file_option=option_syntax(parse_string_or_path.FILE_ARGUMENT_OPTION),
                 rel_symbol_name=expected_file_relativity_symbol),
            ArrangementPostAct(
                tcds_contents=tcds_contents_arrangement,
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
