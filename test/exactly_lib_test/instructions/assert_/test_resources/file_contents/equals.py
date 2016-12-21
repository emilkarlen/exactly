import unittest

from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args, InstructionTestConfigurationForContentsOrEquals, TestWithConfigurationAndNegationArgumentBase, \
    suite_for__conf__not_argument
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    RelativityOptionConfiguration, RelativityOptionConfigurationForRelHome, RelativityOptionConfigurationForRelAct, \
    RelativityOptionConfigurationForRelTmp, \
    MkSubDirOfActAndMakeItCurrentDirectory, TestWithConfigurationAndRelativityOptionAndNegationBase, \
    suite_for__conf__rel_opts__negations, RelativityOptionConfigurationForRelCwdForTestCwdDir
from exactly_lib_test.instructions.assert_.test_resources.file_contents.replace_env_vars_utils import \
    ReplacedEnvVarsFileContentsGenerator
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import svh_check
from exactly_lib_test.test_resources.execution.home_or_sds_populator import HomeOrSdsPopulator
from exactly_lib_test.test_resources.execution.home_or_sds_populator import HomeOrSdsPopulatorForHomeContents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, File
from exactly_lib_test.test_resources.home_and_sds_test import Action


class InstructionTestConfigurationForEquals(InstructionTestConfigurationForContentsOrEquals):
    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: HomeOrSdsPopulator,
                                            post_sds_population_action: Action = Action(),
                                            ) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


def suite_for(instruction_configuration: InstructionTestConfigurationForEquals) -> unittest.TestSuite:
    test_cases_for_rel_opts = [
        _ErrorWhenExpectedFileDoesNotExist,
        _ErrorWhenExpectedFileIsADirectory,
        _ContentsDiffer,
        _ContentsEquals,
        _WhenReplaceEnvVarsOptionIsGivenThenEnVarsShouldBeReplaced,
        _WhenReplaceEnvVarsOptionIsNotGivenThenEnVarsShouldNotBeReplaced,
    ]

    test_cases_without_rel_opts = [
        _ContentsEqualsAHereDocument,
        _ContentsDoNotEqualAHereDocument,
    ]

    return unittest.TestSuite([
        suite_for__conf__rel_opts__negations(instruction_configuration,
                                             _RELATIVITY_OPTION_CONFIGURATIONS,
                                             test_cases_for_rel_opts),
        suite_for__conf__not_argument(instruction_configuration,
                                      test_cases_without_rel_opts),
    ])


class RelativityOptionConfigurationForDefaultRelativityOfExpectedFile(RelativityOptionConfiguration):
    def __init__(self):
        super().__init__('')

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return HomeOrSdsPopulatorForHomeContents(contents)

    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        return Expectation(validation_pre_sds=svh_check.is_validation_error())


_RELATIVITY_OPTION_CONFIGURATIONS = [
    RelativityOptionConfigurationForRelHome(),
    RelativityOptionConfigurationForRelCwdForTestCwdDir(),
    RelativityOptionConfigurationForRelAct(),
    RelativityOptionConfigurationForRelTmp(),
    RelativityOptionConfigurationForDefaultRelativityOfExpectedFile(),
]


class _ErrorWhenExpectedFileDoesNotExist(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} {relativity_option} non-existing-file.txt',
                     maybe_not=self.not_opt.nothing__if_un_negated_else__not_option,
                     relativity_option=self.rel_opt.option_string)),
            ArrangementPostAct(post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            self.rel_opt.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _ErrorWhenExpectedFileIsADirectory(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} {relativity_option} dir',
                     maybe_not=self.not_opt.nothing__if_un_negated_else__not_option,
                     relativity_option=self.rel_opt.option_string)),
            ArrangementPostAct(
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root(
                    DirContents([empty_dir('dir')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()
            ),
            self.rel_opt.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _ContentsDiffer(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} {relativity_option} expected.txt',
                     maybe_not=self.not_opt.nothing__if_un_negated_else__not_option,
                     relativity_option=self.rel_opt.option_string)),
            self.configuration.arrangement_for_actual_and_expected(
                'actual',
                self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('expected.txt', 'expected')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.not_opt.fail__if_un_negated_else__pass),
        )


class _ContentsEquals(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} {relativity_option} expected.txt',
                     maybe_not=self.not_opt.nothing__if_un_negated_else__not_option,
                     relativity_option=self.rel_opt.option_string)),
            self.configuration.arrangement_for_actual_and_expected(
                'expected',
                self.rel_opt.populator_for_relativity_option_root(
                    DirContents([File('expected.txt', 'expected')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.not_opt.pass__if_un_negated_else__fail),
        )


class _WhenReplaceEnvVarsOptionIsGivenThenEnVarsShouldBeReplaced(
    TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        contents_generator = ReplacedEnvVarsFileContentsGenerator()
        self._check(
            self.configuration.source_for(
                args('{replace_env_vars_option} {maybe_not} {equals} {relativity_option} expected.txt',
                     maybe_not=self.not_opt.nothing__if_un_negated_else__not_option,
                     relativity_option=self.rel_opt.option_string)),
            self.configuration.arrangement_for_contents_from_fun(
                contents_generator.contents_before_replacement,
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root_for_contents_from_fun(
                    'expected.txt',
                    contents_generator.expected_contents_after_replacement
                ),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.not_opt.pass__if_un_negated_else__fail),
        )


class _WhenReplaceEnvVarsOptionIsNotGivenThenEnVarsShouldNotBeReplaced(
    TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        contents_generator = ReplacedEnvVarsFileContentsGenerator()

        self._check(
            self.configuration.source_for(
                args('{replace_env_vars_option} {maybe_not} {equals} {relativity_option} expected.txt',
                     maybe_not=self.not_opt.nothing__if_un_negated_else__not_option,
                     relativity_option=self.rel_opt.option_string)),
            self.configuration.arrangement_for_contents_from_fun(
                contents_generator.contents_before_replacement,
                home_or_sds_contents=self.rel_opt.populator_for_relativity_option_root_for_contents_from_fun(
                    'expected.txt',
                    contents_generator.unexpected_contents_after_replacement
                ),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.not_opt.fail__if_un_negated_else__pass),
        )


class _ContentsEqualsAHereDocument(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option),
                ['expected content line',
                 'EOF']),
            self.configuration.arrangement_for_contents(
                lines_content(['expected content line']),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass__if_un_negated_else__fail),
        )


class _ContentsDoNotEqualAHereDocument(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=self.maybe_not.nothing__if_un_negated_else__not_option),
                ['expected content line',
                 'EOF']),
            self.configuration.arrangement_for_contents(
                lines_content(['actual contents that is not equal to expected contents']),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.fail__if_un_negated_else__pass),
        )
