import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib_test.instructions.assert_.contents.test_resources import TestCaseBaseForParser
from exactly_lib_test.instructions.assert_.contents.test_resources import TestConfigurationForFile
from exactly_lib_test.instructions.assert_.test_resources.contents_resources import \
    ActResultProducerForContentsWithAllReplacedEnvVars, \
    StoreContentsInFileInCurrentDir, WriteFileToHomeDir, WriteFileToCurrentDir, \
    StoreContentsInFileInParentDirOfCwd
from exactly_lib_test.instructions.assert_.test_resources.file_contents import equals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.equals import \
    InstructionTestConfigurationForEquals, RelativityOptionConfiguration, RelativityOptionConfigurationForRelCwd, \
    RelativityOptionConfigurationForRelAct, \
    RelativityOptionConfigurationForRelTmp, TestWithConfigurationAndRelativityOptionBase, \
    MkSubDirOfActAndMakeItCurrentDirectory
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, \
    is_pass
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, File, empty_file
from exactly_lib_test.test_resources.parse import new_source2


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestReplacedEnvVars),
        equals.suite_for(TestConfigurationForFile('actual.txt', '../actual.txt')),
        suite_for(TestConfigurationForFile('actual.txt', '../actual.txt')),
    ])


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


_RELATIVITY_OPTION_CONFIGURATIONS = [
    RelativityOptionConfigurationForRelCwd(),
    RelativityOptionConfigurationForRelAct(),
    RelativityOptionConfigurationForRelTmp(),
    # Test of default relativity is done by "generic" tests of equals -
    # i.e. code in the test resources that are used for all content-checking instructions.
]


class _ErrorWhenExpectedFileDoesNotExist(TestWithConfigurationAndRelativityOptionBase):
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


class _ErrorWhenExpectedFileIsADirectory(TestWithConfigurationAndRelativityOptionBase):
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


class TestReplacedEnvVars(TestCaseBaseForParser):
    COMPARISON_EXPECTED_FILE_NAME = 'with-replaced-env-vars.txt'
    COMPARISON_ACTUAL_FILE_NAME = 'file-with-env-var-values-in-it-from-act-phase.txt'

    def source(self, template: str) -> SingleInstructionParserSource:
        _args = args(template,
                     actual_file=self.COMPARISON_ACTUAL_FILE_NAME,
                     expected_file=self.COMPARISON_EXPECTED_FILE_NAME)
        return new_source2(_args)

    def __init__(self,
                 method_name):
        super().__init__(method_name)

    def test_pass__when__contents_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            StoreContentsInFileInCurrentDir(self.COMPARISON_ACTUAL_FILE_NAME),
            source_file_writer=WriteFileToHomeDir(self.COMPARISON_EXPECTED_FILE_NAME),
            source_should_contain_expected_value=True)
        self._run(
            self.source('{actual_file} {replace_env_vars_option} {equals} {rel_home_option} {expected_file}'),
            arrangement(act_result_producer=act_result_producer),
            is_pass(),
        )

    def test_fail__when__contents_not_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            StoreContentsInFileInCurrentDir(self.COMPARISON_ACTUAL_FILE_NAME),
            source_file_writer=WriteFileToHomeDir(self.COMPARISON_EXPECTED_FILE_NAME),
            source_should_contain_expected_value=False)
        self._run(
            self.source('{actual_file} {replace_env_vars_option} {equals} {rel_home_option} {expected_file}'),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__contents_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            StoreContentsInFileInCurrentDir(self.COMPARISON_ACTUAL_FILE_NAME),
            source_file_writer=WriteFileToCurrentDir(self.COMPARISON_EXPECTED_FILE_NAME),
            source_should_contain_expected_value=True)
        self._run(
            self.source('{actual_file} {replace_env_vars_option} {equals} {rel_cwd_option} {expected_file}'),
            arrangement(act_result_producer=act_result_producer),
            is_pass(),
        )

    def test_fail__when__contents_not_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            StoreContentsInFileInCurrentDir(self.COMPARISON_ACTUAL_FILE_NAME),
            source_file_writer=WriteFileToCurrentDir(self.COMPARISON_EXPECTED_FILE_NAME),
            source_should_contain_expected_value=False)
        self._run(
            self.source('{actual_file} {replace_env_vars_option} {equals} {rel_cwd_option} {expected_file}'),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__contents_equals_but_src_does_not_reside_inside_act_dir__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            StoreContentsInFileInParentDirOfCwd(self.COMPARISON_ACTUAL_FILE_NAME),
            source_file_writer=WriteFileToHomeDir(self.COMPARISON_EXPECTED_FILE_NAME),
            source_should_contain_expected_value=True)
        self._run(
            self.source('../{actual_file} {replace_env_vars_option} {equals} {rel_home_option} {expected_file}'),
            arrangement(act_result_producer=act_result_producer),
            is_pass(),
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
