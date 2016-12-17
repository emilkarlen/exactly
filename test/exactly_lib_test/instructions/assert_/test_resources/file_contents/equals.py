import unittest

from exactly_lib.execution import environment_variables
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args, InstructionTestConfigurationForContentsOrEquals, TestWithConfigurationAndNegationArgumentBase, \
    suite_for__conf__not_argument
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    RelativityOptionConfiguration, RelativityOptionConfigurationForRelHome, RelativityOptionConfigurationForRelCwd, \
    RelativityOptionConfigurationForRelAct, RelativityOptionConfigurationForRelTmp, \
    MkSubDirOfActAndMakeItCurrentDirectory, TestWithConfigurationAndRelativityOptionAndNegationBase, \
    suite_for__conf__rel_opts__negations
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
        _FaiWhenContentsDiffer,
        _PassWhenContentsEquals,
        _WhenReplaceEnvVarsOptionIsGivenThenEnVarsShouldBeReplaced,
        _WhenReplaceEnvVarsOptionIsNotGivenThenEnVarsShouldNotBeReplaced,
    ]

    test_cases_without_rel_opts = [
        _PassWhenContentsEqualsAHereDocument,
        _FailWhenContentsDoNotEqualAHereDocument,
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
    RelativityOptionConfigurationForRelCwd(),
    RelativityOptionConfigurationForRelAct(),
    RelativityOptionConfigurationForRelTmp(),
    RelativityOptionConfigurationForDefaultRelativityOfExpectedFile(),
]


class _ErrorWhenExpectedFileDoesNotExist(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} {relativity_option} non-existing-file.txt',
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option(),
                     relativity_option=self.option_configuration.option_string)),
            ArrangementPostAct(post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            self.option_configuration.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _ErrorWhenExpectedFileIsADirectory(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} {relativity_option} dir',
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option(),
                     relativity_option=self.option_configuration.option_string)),
            ArrangementPostAct(
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([empty_dir('dir')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()
            ),
            self.option_configuration.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _FaiWhenContentsDiffer(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} {relativity_option} expected.txt',
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option(),
                     relativity_option=self.option_configuration.option_string)),
            self.configuration.arrangement_for_actual_and_expected(
                'actual',
                self.option_configuration.populator_for_relativity_option_root(
                    DirContents([File('expected.txt', 'expected')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.fail_if_un_negated_else_pass()),
        )


class _PassWhenContentsEquals(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} {relativity_option} expected.txt',
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option(),
                     relativity_option=self.option_configuration.option_string)),
            self.configuration.arrangement_for_actual_and_expected(
                'expected',
                self.option_configuration.populator_for_relativity_option_root(
                    DirContents([File('expected.txt', 'expected')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass_if_not_negated_else_fail()),
        )


class _WhenReplaceEnvVarsOptionIsGivenThenEnVarsShouldBeReplaced(
    TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        def home_dir_path_name(home_and_sds: HomeAndSds):
            return str(home_and_sds.home_dir_path)

        self._check(
            self.configuration.source_for(
                args('{replace_env_vars_option} {maybe_not} {equals} {relativity_option} expected.txt',
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option(),
                     relativity_option=self.option_configuration.option_string)),
            self.configuration.arrangement_for_contents_from_fun(
                home_dir_path_name,
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([File('expected.txt', environment_variables.ENV_VAR_HOME)])
                ),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass_if_not_negated_else_fail()),
        )


class _WhenReplaceEnvVarsOptionIsNotGivenThenEnVarsShouldNotBeReplaced(
    TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        def home_dir_path_name(home_and_sds: HomeAndSds):
            return str(home_and_sds.home_dir_path)

        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} {relativity_option} expected.txt',
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option(),
                     relativity_option=self.option_configuration.option_string)),
            self.configuration.arrangement_for_contents_from_fun(
                home_dir_path_name,
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([File('expected.txt', environment_variables.ENV_VAR_HOME)])
                ),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.fail_if_un_negated_else_pass()),
        )


class _PassWhenContentsEqualsAHereDocument(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option()),
                ['expected content line',
                 'EOF']),
            self.configuration.arrangement_for_contents(
                lines_content(['expected content line']),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass_if_not_negated_else_fail()),
        )


class _FailWhenContentsDoNotEqualAHereDocument(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{maybe_not} {equals} <<EOF',
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option()),
                ['expected content line',
                 'EOF']),
            self.configuration.arrangement_for_contents(
                lines_content(['actual contents that is not equal to expected contents']),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.fail_if_un_negated_else_pass()),
        )
