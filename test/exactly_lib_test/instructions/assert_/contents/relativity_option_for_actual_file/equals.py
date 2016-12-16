import unittest

from exactly_lib_test.instructions.assert_.contents.relativity_option_for_actual_file.test_resources import \
    suite_for_all_relativity_options
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    TestWithConfigurationAndRelativityOptionBase, MkSubDirOfActAndMakeItCurrentDirectory
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, File, empty_file
from exactly_lib_test.test_resources.parse import new_source2


def suite_for(instruction_configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return suite_for_all_relativity_options(instruction_configuration,
                                            [
                                                _ErrorWhenActualFileDoesNotExist,
                                                _ErrorWhenActualFileIsADirectory,
                                                _FaiWhenContentsDiffer,
                                                _PassWhenContentsEquals,
                                            ]
                                            )


class _ErrorWhenActualFileDoesNotExist(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            new_source2(
                args('{relativity_option} actual.txt {equals} {rel_home_option} expected.txt',
                     relativity_option=self.option_configuration.option_string)),
            ArrangementPostAct(
                home_contents=DirContents([empty_file('expected.txt')]),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            self.option_configuration.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _ErrorWhenActualFileIsADirectory(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            new_source2(
                args('{relativity_option} actual-dir {equals} {rel_home_option} expected.txt',
                     relativity_option=self.option_configuration.option_string)),
            ArrangementPostAct(
                home_contents=DirContents([File('expected.txt', 'expected contents')]),
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([empty_dir('actual-dir')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            self.option_configuration.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _FaiWhenContentsDiffer(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            new_source2(
                args('{relativity_option} actual.txt {equals} {rel_home_option} expected.txt',
                     relativity_option=self.option_configuration.option_string)),
            ArrangementPostAct(
                home_contents=DirContents([File('expected.txt', 'expected contents')]),
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', 'not equal to expected contents')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_fail()),
        )


class _PassWhenContentsEquals(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            new_source2(
                args('{relativity_option} actual.txt {equals} {rel_home_option} expected.txt',
                     relativity_option=self.option_configuration.option_string)),
            ArrangementPostAct(
                home_contents=DirContents([File('expected.txt', 'expected contents')]),
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', 'expected contents')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_pass()),
        )
