import os
import unittest

from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args, InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    RelativityOptionConfiguration, TestWithConfigurationAndRelativityOptionBase, \
    RelativityOptionConfigurationForRelHome, RelativityOptionConfigurationForRelCwd, \
    RelativityOptionConfigurationForRelAct, RelativityOptionConfigurationForRelTmp, \
    _get_cwd_path_and_make_dir_if_not_exists
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check, svh_check
from exactly_lib_test.test_resources import home_and_sds_test
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
    def suite_for_option(option_configuration: RelativityOptionConfiguration) -> unittest.TestSuite:
        test_cases = [
            _ErrorWhenExpectedFileDoesNotExist,
            _ErrorWhenExpectedFileIsADirectory,
            _FaiWhenContentsDiffer,
            _PassWhenContentsEquals,
        ]
        return unittest.TestSuite([tc(instruction_configuration, option_configuration)
                                   for tc in test_cases])

    return unittest.TestSuite([suite_for_option(relativity_option_configuration)
                               for relativity_option_configuration in _RELATIVITY_OPTION_CONFIGURATIONS])


class MkSubDirOfActAndMakeItCurrentDirectory(home_and_sds_test.Action):
    def apply(self, home_and_sds: HomeAndSds):
        sub_dir = _get_cwd_path_and_make_dir_if_not_exists(home_and_sds.sds)
        os.chdir(str(sub_dir))


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


class _ErrorWhenExpectedFileDoesNotExist(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{equals} {relativity_option} non-existing-file.txt',
                     relativity_option=self.option_configuration.option_string)),
            ArrangementPostAct(post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            self.option_configuration.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _ErrorWhenExpectedFileIsADirectory(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{equals} {relativity_option} dir',
                     relativity_option=self.option_configuration.option_string)),
            ArrangementPostAct(
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([empty_dir('dir')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()
            ),
            self.option_configuration.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _FaiWhenContentsDiffer(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{equals} {relativity_option} expected.txt',
                     relativity_option=self.option_configuration.option_string)),
            self.configuration.arrangement_for_actual_and_expected(
                'actual',
                self.option_configuration.populator_for_relativity_option_root(
                    DirContents([File('expected.txt', 'expected')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_fail()),
        )


class _PassWhenContentsEquals(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{equals} {relativity_option} expected.txt',
                     relativity_option=self.option_configuration.option_string)),
            self.configuration.arrangement_for_actual_and_expected(
                'expected',
                self.option_configuration.populator_for_relativity_option_root(
                    DirContents([File('expected.txt', 'expected')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_pass()),
        )
