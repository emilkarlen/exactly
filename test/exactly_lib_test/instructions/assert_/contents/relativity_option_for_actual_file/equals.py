import unittest

from exactly_lib.instructions.assert_.utils.file_contents.contents_utils_for_instr_doc import \
    EXPECTED_FILE_REL_OPT_ARG_CONFIG
from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsNothing
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.instructions.assert_.contents.relativity_option_for_actual_file.test_resources import \
    RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    suite_for__conf__rel_opts__negations, TestWithConfigurationAndRelativityOptionAndNegationBase, \
    MkSubDirOfActAndMakeItCurrentDirectory
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.concrete_restriction_assertion import equals_file_ref_relativity_restriction
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_reference
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, File, empty_file
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(instruction_configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return suite_for__conf__rel_opts__negations(instruction_configuration,
                                                RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE,
                                                [
                                                    _ErrorWhenActualFileDoesNotExist,
                                                    _ErrorWhenActualFileIsADirectory,
                                                    _ContentsDiffer,
                                                    _ContentsEquals,
                                                    _ContentsEqualsWithExpectedFileRelHomeSymbol,
                                                    _ContentsEqualsWithExpectedFileRelTmpSymbol,
                                                ]
                                                )


class _ErrorWhenActualFileDoesNotExist(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {maybe_not} {equals} {rel_home_option} expected.txt',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_un_negated_else__not_option),
            ArrangementPostAct(
                home_contents=DirContents([empty_file('expected.txt')]),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory(),
                symbols=self.rel_opt.symbols_in_arrangement(),
            ),
            self.rel_opt.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _ErrorWhenActualFileIsADirectory(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual-dir {maybe_not} {equals} {rel_home_option} expected.txt',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_un_negated_else__not_option),
            ArrangementPostAct(
                home_contents=DirContents([File('expected.txt', 'expected contents')]),
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([empty_dir('actual-dir')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory(),
                symbols=self.rel_opt.symbols_in_arrangement(),
            ),
            self.rel_opt.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _ContentsDiffer(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {maybe_not} {equals} {rel_home_option} expected.txt',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_un_negated_else__not_option),
            ArrangementPostAct(
                home_contents=DirContents([File('expected.txt', 'expected contents')]),
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', 'not equal to expected contents')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory(),
                symbols=self.rel_opt.symbols_in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.fail__if_un_negated_else__pass,
                symbol_usages=self.rel_opt.symbol_usages_expectation(),
            ),
        )


class _ContentsEquals(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {maybe_not} {equals} {rel_home_option} expected.txt',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_un_negated_else__not_option),
            ArrangementPostAct(
                home_contents=DirContents([File('expected.txt', 'expected contents')]),
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', 'expected contents')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory(),
                symbols=self.rel_opt.symbols_in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.pass__if_un_negated_else__fail,
                symbol_usages=self.rel_opt.symbol_usages_expectation(),
            ),
        )


class _ContentsEqualsWithExpectedRelSymbolBase(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def relativity_of_expected_file(self) -> RelOptionType:
        raise NotImplementedError()

    def runTest(self):
        expected_file_relativity_symbol = 'EXPECTED_RELATIVITY_SYMBOL_NAME'
        file_ref_sym_tbl_entry_for_expected_file = symbol_utils.entry(
            expected_file_relativity_symbol,
            FileRefConstant(file_refs.of_rel_option(self.relativity_of_expected_file(),
                                                    PathPartAsNothing())))

        symbols_in_arrangement = symbol_utils.symbol_table_from_entries(
            [file_ref_sym_tbl_entry_for_expected_file] +
            self.rel_opt.symbol_entries_for_arrangement())

        symbol_usage_expectation_for_expected_file = equals_symbol_reference(
            expected_file_relativity_symbol,
            equals_file_ref_relativity_restriction(
                FileRefRelativityRestriction(
                    EXPECTED_FILE_REL_OPT_ARG_CONFIG.options.accepted_relativity_variants)))

        expected_symbol_usages = asrt.matches_sequence(
            [symbol_usage_expectation_for_expected_file] +
            self.rel_opt.symbol_usage_expectation_assertions())

        populator_of_expected_files = home_and_sds_populators.HomeOrSdsPopulatorForRelOptionType(
            self.relativity_of_expected_file(),
            DirContents([File('expected.txt', 'expected contents')]))
        populator_of_actual_files = self.rel_opt.populator_for_relativity_option_root(
            DirContents([File('actual.txt', 'expected contents')]))
        home_or_sds_contents_arrangement = home_and_sds_populators.multiple([
            populator_of_actual_files,
            populator_of_expected_files
        ])
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {maybe_not} {equals} '
                 '{rel_symbol_option} {rel_symbol_name} expected.txt',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_un_negated_else__not_option,
                 rel_symbol_name=expected_file_relativity_symbol),
            ArrangementPostAct(
                home_or_sds_contents=home_or_sds_contents_arrangement,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory(),
                symbols=symbols_in_arrangement,
            ),
            Expectation(
                main_result=self.not_opt.pass__if_un_negated_else__fail,
                symbol_usages=expected_symbol_usages,
            ),
        )


class _ContentsEqualsWithExpectedFileRelHomeSymbol(_ContentsEqualsWithExpectedRelSymbolBase):
    def relativity_of_expected_file(self) -> RelOptionType:
        return RelOptionType.REL_HOME


class _ContentsEqualsWithExpectedFileRelTmpSymbol(_ContentsEqualsWithExpectedRelSymbolBase):
    def relativity_of_expected_file(self) -> RelOptionType:
        return RelOptionType.REL_TMP
