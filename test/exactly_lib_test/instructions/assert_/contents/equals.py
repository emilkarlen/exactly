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
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import args
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, \
    Expectation, is_pass
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check, svh_check
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents, tmp_user_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, File
from exactly_lib_test.test_resources.parse import new_source2


class TestFileExpectedFileRelHome(TestCaseBaseForParser):
    def test_fail__when__actual_file_does_not_exist(self):
        self._run(
            new_source2(args('name-of-non-existing-file {equals} {rel_home_option} expected.txt')),
            arrangement(home_dir_contents=DirContents([empty_file('expected.txt')])),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_validation_error__when__actual_file_is_a_directory(self):
        self._run(
            new_source2(args('name-of-non-existing-file {equals} {rel_home_option} dir')),
            arrangement(home_dir_contents=DirContents([empty_dir('dir')])),
            Expectation(validation_pre_sds=svh_check.is_validation_error()),
        )


class TestFileExpectedFileRelCwd(TestCaseBaseForParser):
    def test_fail__when__actual_file_does_not_exist(self):
        self._run(
            new_source2(args('target {equals} {rel_cwd_option} expected.txt')),
            arrangement(sds_contents_before_main=act_dir_contents(
                DirContents([empty_file('expected.txt')]))),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail__when__actual_file_is_a_directory(self):
        self._run(
            new_source2(args('target {equals} {rel_cwd_option} expected.txt')),
            arrangement(sds_contents_before_main=act_dir_contents(
                DirContents([empty_dir('target'),
                             empty_file('expected.txt')]))),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestFileExpectedFileRelTmp(TestCaseBaseForParser):
    def test_fail__when__actual_file_does_not_exist(self):
        self._run(
            new_source2(args('target {equals} {rel_tmp_option} expected.txt')),
            arrangement(sds_contents_before_main=tmp_user_dir_contents(
                DirContents([empty_file('expected.txt')]))),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestExpectedFileRelTmp(TestCaseBaseForParser):
    def test_fail__when__actual_file_does_not_exist(self):
        self._run(
            new_source2(args('{rel_tmp_option} actual.txt {equals} {rel_home_option} expected.txt')),
            arrangement(home_dir_contents=DirContents([empty_file('expected.txt')])),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__contents_is_equal(self):
        self._run(
            new_source2(args('{rel_tmp_option} actual.txt {equals} {rel_home_option} expected.txt')),
            arrangement(home_dir_contents=DirContents([File('expected.txt', 'contents')]),
                        sds_contents_before_main=tmp_user_dir_contents(
                            DirContents([File('actual.txt', 'contents')]))),
            is_pass(),
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


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileExpectedFileRelHome),
        unittest.makeSuite(TestFileExpectedFileRelCwd),
        unittest.makeSuite(TestFileExpectedFileRelTmp),
        unittest.makeSuite(TestExpectedFileRelTmp),
        unittest.makeSuite(TestReplacedEnvVars),
        equals.suite_for(TestConfigurationForFile('actual.txt', '../actual.txt'))
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
