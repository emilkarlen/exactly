import unittest

from exactly_lib_test.instructions.assert_.contents.relativity_option_for_actual_file.test_resources import \
    RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args, InstructionTestConfiguration
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    MkSubDirOfActAndMakeItCurrentDirectory, TestWithConfigurationAndRelativityOptionAndNegationBase, \
    suite_for__conf__rel_opts__negations
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, File
from exactly_lib_test.test_resources.parse import new_source2


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
        self._check(
            new_source2(
                args('{relativity_option} actual.txt {maybe_not} {empty}',
                     relativity_option=self.option_configuration.option_string,
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())),
            ArrangementPostAct(
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            self.option_configuration.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _ErrorWhenActualFileIsADirectory(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check(
            new_source2(
                args('{relativity_option} actual-dir {maybe_not} {empty}',
                     relativity_option=self.option_configuration.option_string,
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())),
            ArrangementPostAct(
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([empty_dir('actual-dir')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            self.option_configuration.expectation_that_file_for_expected_contents_is_invalid(),
        )


class _ContentsIsNotEmpty(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check(
            new_source2(
                args('{relativity_option} actual.txt {maybe_not} {empty}',
                     relativity_option=self.option_configuration.option_string,
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())),
            ArrangementPostAct(
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', 'not empty contents')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.fail_if_un_negated_else_pass()),
        )


class _ContentsIsEmpty(TestWithConfigurationAndRelativityOptionAndNegationBase):
    def runTest(self):
        self._check(
            new_source2(
                args('{relativity_option} actual.txt {maybe_not} {empty}',
                     relativity_option=self.option_configuration.option_string,
                     maybe_not=self.maybe_not.nothing_if_un_negated_else_not_option())),
            ArrangementPostAct(
                home_or_sds_contents=self.option_configuration.populator_for_relativity_option_root(
                    DirContents([File('actual.txt', '')])),
                post_sds_population_action=MkSubDirOfActAndMakeItCurrentDirectory()),
            Expectation(main_result=self.maybe_not.pass_if_not_negated_else_fail()),
        )
