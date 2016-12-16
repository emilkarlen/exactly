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
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, File
from exactly_lib_test.test_resources.parse import new_source2


def suite_for(instruction_configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return suite_for_all_relativity_options(instruction_configuration,
                                            [
                                                _ErrorWhenActualFileDoesNotExist,
                                                _ErrorWhenActualFileIsADirectory,
                                                _FaiWhenContentsDoesNotContainALineThatMatches,
                                                _PassWhenContentsContainsALineThatMatches,
                                            ]
                                            )


class _ErrorWhenActualFileDoesNotExist(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            new_source2(
                args('{relativity_option} actual.txt {contains} REG.*EX',
                     relativity_option=self.option_configuration.option_string)),
            ArrangementPostAct(
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            self.option_configuration.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _ErrorWhenActualFileIsADirectory(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            new_source2(
                args('{relativity_option} actual-dir {contains} REG.*EX',
                     relativity_option=self.option_configuration.option_string)),
            ArrangementPostAct(
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([empty_dir('actual-dir')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            self.option_configuration.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _FaiWhenContentsDoesNotContainALineThatMatches(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            new_source2(
                args('{relativity_option} actual.txt {contains} REG.*EX',
                     relativity_option=self.option_configuration.option_string)),
            ArrangementPostAct(
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', 'no match')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_fail()),
        )


class _PassWhenContentsContainsALineThatMatches(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            new_source2(
                args('{relativity_option} actual.txt {contains} REG.*EX',
                     relativity_option=self.option_configuration.option_string)),
            ArrangementPostAct(
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', 'REG-matching-EX')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=pfh_check.is_pass()),
        )
