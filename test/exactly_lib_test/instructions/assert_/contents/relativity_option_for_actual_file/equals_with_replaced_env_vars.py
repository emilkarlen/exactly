import unittest

from exactly_lib_test.instructions.assert_.contents.relativity_option_for_actual_file.test_resources import \
    RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    suite_for__conf__rel_opts__negations, TestWithConfigurationAndRelativityOptionAndNegationBase, \
    MkSubDirOfActAndMakeItCurrentDirectory
from exactly_lib_test.instructions.assert_.test_resources.file_contents.replace_env_vars_utils import \
    ReplacedEnvVarsFileContentsGenerator
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.relativity_options import RelativityOptionConfigurationForRelTmp
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import multiple


def suite_for(instruction_configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return suite_for__conf__rel_opts__negations(instruction_configuration,
                                                RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE,
                                                [
                                                    _ContentsEquals,
                                                    _ContentsNotEquals,
                                                ]
                                                )


class _ContentsEquals(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        contents_generator = ReplacedEnvVarsFileContentsGenerator()
        rel_tmp_opt = RelativityOptionConfigurationForRelTmp()
        populator_of_expected = rel_tmp_opt.populator_for_relativity_option_root_for_contents_from_fun(
            'expected.txt',
            contents_generator.expected_contents_after_replacement)
        populator_of_actual = self.rel_opt.populator_for_relativity_option_root_for_contents_from_fun(
            'actual.txt',
            contents_generator.contents_before_replacement)
        home_or_sds_populator = multiple([populator_of_expected, populator_of_actual])
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {replace_env_vars_option} '
                 '{maybe_not} {equals} {rel_tmp_option} expected.txt',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_un_negated_else__not_option),
            ArrangementPostAct(
                home_or_sds_contents=home_or_sds_populator,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.not_opt.pass__if_un_negated_else__fail),
        )


class _ContentsNotEquals(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        contents_generator = ReplacedEnvVarsFileContentsGenerator()
        rel_tmp_opt = RelativityOptionConfigurationForRelTmp()
        populator_of_expected = rel_tmp_opt.populator_for_relativity_option_root_for_contents_from_fun(
            'expected.txt',
            contents_generator.unexpected_contents_after_replacement)
        populator_of_actual = self.rel_opt.populator_for_relativity_option_root_for_contents_from_fun(
            'actual.txt',
            contents_generator.contents_before_replacement)
        home_or_sds_populator = multiple([populator_of_expected, populator_of_actual])
        self._check_single_instruction_line_with_source_variants(
            args('{relativity_option} actual.txt {replace_env_vars_option} '
                 '{maybe_not} {equals} {rel_tmp_option} expected.txt',
                 relativity_option=self.rel_opt.option_string,
                 maybe_not=self.not_opt.nothing__if_un_negated_else__not_option),
            ArrangementPostAct(
                home_or_sds_contents=home_or_sds_populator,
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.not_opt.fail__if_un_negated_else__pass),
        )
