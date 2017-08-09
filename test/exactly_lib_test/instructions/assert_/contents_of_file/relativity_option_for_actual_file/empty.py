import unittest

from exactly_lib_test.instructions.assert_.contents_of_file.relativity_option_for_actual_file.test_resources import \
    RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE
from exactly_lib_test.instructions.assert_.test_resources.file_contents.expectation_utils import \
    expectation_that_file_for_expected_contents_is_invalid
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    suite_for__conf__rel_opts__negations, TestWithConfigurationAndRelativityOptionAndNegationBase, \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, File


def suite_for(instruction_configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    test_cases = [
        _ErrorWhenActualFileDoesNotExist,
        _ErrorWhenActualFileIsADirectory,
        _ContentsIsNotEmpty,
        _ContentsIsEmpty,
    ]
    return suite_for__conf__rel_opts__negations(instruction_configuration,
                                                RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE,
                                                test_cases)


class _ErrorWhenActualFileDoesNotExist(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {maybe_not} {empty}',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_un_negated_else__not_option),
            ArrangementPostAct(
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            expectation_that_file_for_expected_contents_is_invalid(self.rel_opt),
        )


class _ErrorWhenActualFileIsADirectory(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual-dir {maybe_not} {empty}',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_un_negated_else__not_option),
            ArrangementPostAct(
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([empty_dir('actual-dir')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            expectation_that_file_for_expected_contents_is_invalid(self.rel_opt),
        )


class _ContentsIsNotEmpty(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {maybe_not} {empty}',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_un_negated_else__not_option),
            ArrangementPostAct(
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', 'not empty contents')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.fail__if_un_negated_else__pass,
                symbol_usages=self.rel_opt.symbols.usages_expectation(),
            ),
        )


class _ContentsIsEmpty(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {maybe_not} {empty}',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_un_negated_else__not_option),
            ArrangementPostAct(
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', '')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.pass__if_un_negated_else__fail,
                symbol_usages=self.rel_opt.symbols.usages_expectation(),
            ),
        )
