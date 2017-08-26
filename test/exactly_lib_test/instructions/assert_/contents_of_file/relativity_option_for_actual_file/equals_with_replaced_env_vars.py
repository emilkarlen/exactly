import unittest

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.instructions.assert_.contents_of_file.relativity_option_for_actual_file.test_resources import \
    RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE
from exactly_lib_test.instructions.assert_.test_resources.file_contents.arrangement_utils import \
    populator_for_relativity_option_root_for_contents_from_fun
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    suite_for__conf__rel_opts__negations, TestWithConfigurationAndRelativityOptionAndNegationBase, \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources import relativity_options as rel_opt
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import multiple
from exactly_lib_test.type_system_values.file_transformers.test_resources import \
    ReplacedEnvVarsFileContentsGeneratorWithAllReplacedVariables


def suite_for(instruction_configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return suite_for__conf__rel_opts__negations(instruction_configuration,
                                                RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE,
                                                [
                                                    _ContentsEquals,
                                                    _ContentsNotEquals,
                                                ]
                                                )


class _ContentsEqualsWhenRelHomeCaseIsSubDirOfRelHomeAct(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        contents_generator = ReplacedEnvVarsFileContentsGeneratorWithAllReplacedVariables()
        rel_tmp_opt = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
        populator_of_expected = populator_for_relativity_option_root_for_contents_from_fun(
            rel_tmp_opt,
            'expected.txt',
            contents_generator.expected_contents_after_replacement)
        populator_of_actual = populator_for_relativity_option_root_for_contents_from_fun(
            self.rel_opt,
            'actual.txt',
            contents_generator.contents_before_replacement)
        home_or_sds_populator = multiple([populator_of_expected, populator_of_actual])
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {replace_env_vars_option} '
                 '{maybe_not} {equals} {rel_tmp_option} expected.txt',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative),
            ArrangementPostAct(
                home_or_sds_contents=home_or_sds_populator,
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.pass__if_positive__fail__if_negative,
                symbol_usages=self.rel_opt.symbols.usages_expectation(),
            ),
        )


class _ContentsEquals(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        contents_generator = ReplacedEnvVarsFileContentsGeneratorWithAllReplacedVariables()
        rel_tmp_opt = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
        populator_of_expected = populator_for_relativity_option_root_for_contents_from_fun(
            rel_tmp_opt,
            'expected.txt',
            contents_generator.expected_contents_after_replacement)
        populator_of_actual = populator_for_relativity_option_root_for_contents_from_fun(
            self.rel_opt,
            'actual.txt',
            contents_generator.contents_before_replacement)
        home_or_sds_populator = multiple([populator_of_expected, populator_of_actual])
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {replace_env_vars_option} '
                 '{maybe_not} {equals} {rel_tmp_option} expected.txt',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative),
            ArrangementPostAct(
                home_or_sds_contents=home_or_sds_populator,
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.pass__if_positive__fail__if_negative,
                symbol_usages=self.rel_opt.symbols.usages_expectation(),
            ),
        )


class _ContentsNotEquals(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        contents_generator = ReplacedEnvVarsFileContentsGeneratorWithAllReplacedVariables()
        rel_tmp_opt = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
        populator_of_expected = populator_for_relativity_option_root_for_contents_from_fun(
            rel_tmp_opt,
            'expected.txt',
            contents_generator.unexpected_contents_after_replacement)
        populator_of_actual = populator_for_relativity_option_root_for_contents_from_fun(
            self.rel_opt,
            'actual.txt',
            contents_generator.contents_before_replacement)
        home_or_sds_populator = multiple([populator_of_expected, populator_of_actual])
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {replace_env_vars_option} '
                 '{maybe_not} {equals} {rel_tmp_option} expected.txt',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_positive__not_option__if_negative),
            ArrangementPostAct(
                home_or_sds_contents=home_or_sds_populator,
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=self.rel_opt.symbols.in_arrangement(),
            ),
            Expectation(
                main_result=self.not_opt.fail__if_positive__pass_if_negative,
                symbol_usages=self.rel_opt.symbols.usages_expectation(),
            ),
        )
