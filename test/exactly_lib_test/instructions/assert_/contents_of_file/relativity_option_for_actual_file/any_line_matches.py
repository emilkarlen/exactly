import unittest

from exactly_lib.util.logic_types import Quantifier
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
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.line_matcher.test_resources.argument_syntax import syntax_for_regex_matcher
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import \
    LineMatchesAssertionArgumentsConstructor
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.misc import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir, File


def suite_for(instruction_configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return suite_for__conf__rel_opts__negations(instruction_configuration,
                                                RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE,
                                                [
                                                    _ErrorWhenActualFileDoesNotExist,
                                                    _ErrorWhenActualFileIsADirectory,
                                                    _ContentsDoesNotContainALineThatMatches,
                                                    _ContentsContainsALineThatMatches,
                                                ]
                                                )


class _ErrorWhenActualFileDoesNotExist(TestWithConfigurationAndRelativityOptionAndNegationForConstArgsBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            '{relativity_option} actual.txt {maybe_not} {regex_line_matcher}'.format(
                relativity_option=self.rel_opt.option_argument,
                maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                regex_line_matcher=exists_line_matches_reg_ex('REG.*EX'),
            ),
            ArrangementPostAct(
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            expectation_that_file_for_actual_contents_is_invalid(self.rel_opt),
        )


class _ErrorWhenActualFileIsADirectory(TestWithConfigurationAndRelativityOptionAndNegationForConstArgsBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            '{relativity_option} actual-dir {maybe_not} {regex_line_matcher}'.format(
                relativity_option=self.rel_opt.option_argument,
                maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                regex_line_matcher=exists_line_matches_reg_ex('REG.*EX'),
            ),
            ArrangementPostAct(
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([empty_dir('actual-dir')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            expectation_that_file_for_actual_contents_is_invalid(self.rel_opt),
        )


class _ContentsDoesNotContainALineThatMatches(TestWithConfigurationAndRelativityOptionAndNegationForConstArgsBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            '{relativity_option} actual.txt {maybe_not} {regex_line_matcher}'.format(
                relativity_option=self.rel_opt.option_argument,
                maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                regex_line_matcher=exists_line_matches_reg_ex('REG.*EX'),
            ),
            ArrangementPostAct(
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', 'no match')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.fail__if_positive__pass_if_negative,
                symbol_usages=self.rel_opt.symbols.usages_expectation(),
            ),
        )


class _ContentsContainsALineThatMatches(TestWithConfigurationAndRelativityOptionAndNegationForConstArgsBase):
    def runTest(self):
        self._check_single_instruction_line_with_source_variants(
            '{relativity_option} actual.txt {maybe_not} {regex_line_matcher}'.format(
                relativity_option=self.rel_opt.option_argument,
                maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative,
                regex_line_matcher=exists_line_matches_reg_ex('REG.*EX'),
            ),
            ArrangementPostAct(
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', 'REG-matching-EX')])),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.pass__if_positive__fail__if_negative,
                symbol_usages=self.rel_opt.symbols.usages_expectation(),
            ),
        )


def exists_line_matches_reg_ex(regex: str) -> str:
    return str(LineMatchesAssertionArgumentsConstructor(Quantifier.EXISTS,
                                                        syntax_for_regex_matcher(regex)))
