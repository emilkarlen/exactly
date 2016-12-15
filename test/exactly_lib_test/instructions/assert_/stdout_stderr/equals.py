import unittest

from exactly_lib.instructions.assert_ import stdout_stderr as sut
from exactly_lib.instructions.assert_.utils.file_contents.parsing import EQUALS_ARGUMENT
from exactly_lib.instructions.utils.arg_parse import relative_path_options
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.assert_.stdout_stderr.test_resources import TestWithParserBase, \
    TestConfigurationForStdout, TestConfigurationForStderr
from exactly_lib_test.instructions.assert_.test_resources.contents_resources import \
    ActResultProducerForContentsWithAllReplacedEnvVars, \
    OutputContentsToStdout, WriteFileToHomeDir, ActResultContentsSetup, OutputContentsToStderr, WriteFileToCurrentDir
from exactly_lib_test.instructions.assert_.test_resources.file_contents.contains import TestWithConfigurationBase
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestConfiguration, args
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, Expectation, is_pass
from exactly_lib_test.instructions.test_resources.arrangements import ActResultProducerFromActResult, ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check, svh_check
from exactly_lib_test.test_resources.execution.home_or_sds_populator import HomeOrSdsPopulatorForHomeContents, \
    HomeOrSdsPopulator
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents, tmp_user_dir_contents
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, File
from exactly_lib_test.test_resources.parse import new_source2, argument_list_source


class RelativityOptionConfiguration:
    def __init__(self, cli_option: str):
        self.cli_option = cli_option

    def contents_at_option_relativity_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        raise NotImplementedError()


class TestWithConfigurationAndRelativityOptionBase(TestWithConfigurationBase):
    def __init__(self,
                 instruction_configuration: TestConfiguration,
                 option_configuration: RelativityOptionConfiguration):
        super().__init__(instruction_configuration)
        self.option_configuration = option_configuration


class RelativityOptionConfigurationForRelHome(RelativityOptionConfiguration):
    def __init__(self):
        super().__init__(relative_path_options.REL_HOME_OPTION)

    def contents_at_option_relativity_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return HomeOrSdsPopulatorForHomeContents(contents)


class _ValidationErrorWhenComparisonFileDoesNotExist(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{equals} {relativity_option} non-existing-file.txt',
                     relativity_option=self.option_configuration.cli_option)),
            ArrangementPostAct(),
            Expectation(validation_pre_sds=svh_check.is_validation_error()),
        )


class _ValidationErrorWhenComparisonFileIsADirectory(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{equals} {relativity_option} dir',
                     relativity_option=self.option_configuration.cli_option)),
            ArrangementPostAct(
                home_or_sds_contents=self.option_configuration.contents_at_option_relativity_root(
                    DirContents([empty_dir('dir')]))),
            Expectation(validation_pre_sds=svh_check.is_validation_error()),
        )


class _FaiWhenContentsDiffer(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{equals} {relativity_option} f.txt',
                     relativity_option=self.option_configuration.cli_option)),
            self.configuration.arrangement_for_actual_and_expected(
                'actual',
                self.option_configuration.contents_at_option_relativity_root(
                    DirContents([File('f.txt', 'expected')]))),
            Expectation(main_result=pfh_check.is_fail()),
        )


class _PassWhenContentsEquals(TestWithConfigurationAndRelativityOptionBase):
    def runTest(self):
        self._check(
            self.configuration.source_for(
                args('{equals} {relativity_option} f.txt',
                     relativity_option=self.option_configuration.cli_option)),
            self.configuration.arrangement_for_actual_and_expected(
                'expected',
                self.option_configuration.contents_at_option_relativity_root(
                    DirContents([File('f.txt', 'expected')]))),
            Expectation(main_result=pfh_check.is_pass()),
        )


class FileContentsFileRelCwd(TestWithParserBase):
    def fail__when__comparison_file_does_not_exist(self):
        self._run(
            new_source2(args('{equals} {rel_cwd_option} f.txt')),
            arrangement(),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def fail__when__comparison_file_is_a_directory(self):
        self._run(
            new_source2(args('{equals} {rel_cwd_option} dir')),
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_dir('dir')]))),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def fail__when__contents_differ(self,
                                    act_result: ActResult,
                                    expected_contents: str):
        self._run(
            new_source2(args('{equals} {rel_cwd_option} f.txt')),
            arrangement(
                sds_contents_before_main=act_dir_contents(DirContents(
                    [File('f.txt', expected_contents)])),
                act_result_producer=ActResultProducerFromActResult(act_result)),
            Expectation(
                main_result=pfh_check.is_fail()),
        )

    def pass__when__contents_equals(self,
                                    act_result: ActResult,
                                    expected_contents: str):
        self._run(
            new_source2(args('{equals} {rel_cwd_option} f.txt')),
            arrangement(
                sds_contents_before_main=act_dir_contents(DirContents(
                    [File('f.txt', expected_contents)])),
                act_result_producer=ActResultProducerFromActResult(act_result)),
            is_pass(),
        )


class FileContentsFileRelTmp(TestWithParserBase):
    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        raise NotImplementedError()

    def fail__when__comparison_file_does_not_exist(self):
        self._run(
            new_source2(args('{equals} {rel_tmp_option}  f.txt')),
            arrangement(),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def pass__when__contents_equals(self):
        self._run(
            new_source2(args('{equals} {rel_tmp_option}  f.txt')),
            arrangement(
                sds_contents_before_main=tmp_user_dir_contents(DirContents(
                    [File('f.txt', 'expected contents')])),
                act_result_producer=ActResultProducerFromActResult(
                    self._act_result_with_contents('expected contents'))),
            is_pass(),
        )


class FileContentsHereDoc(TestWithParserBase):
    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        raise NotImplementedError()

    def pass__when__contents_equals(self):
        self._run(
            argument_list_source([EQUALS_ARGUMENT, '<<EOF'],
                                 ['single line',
                                  'EOF']),
            arrangement(act_result_producer=ActResultProducerFromActResult(
                self._act_result_with_contents(lines_content(['single line'])))),
            is_pass(),
        )


class TestFileContentsFileRelCwdFORStdout(FileContentsFileRelCwd):
    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def test_fail__when__comparison_file_does_not_exist(self):
        self.fail__when__comparison_file_does_not_exist()

    def test_fail__when__comparison_file_is_a_directory(self):
        self.fail__when__comparison_file_is_a_directory()

    def test_fail__when__contents_differ(self):
        self.fail__when__contents_differ(ActResult(stdout_contents='un-expected',
                                                   stderr_contents='expected'),
                                         'expected')

    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals(ActResult(stdout_contents='expected',
                                                   stderr_contents='un-expected'),
                                         'expected')


class TestFileContentsFileRelCwdFORStderr(FileContentsFileRelCwd):
    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def test_validation_error__when__comparison_file_does_not_exist(self):
        self.fail__when__comparison_file_does_not_exist()

    def test_validation_error__when__comparison_file_is_a_directory(self):
        self.fail__when__comparison_file_is_a_directory()

    def test_fail__when__contents_differ(self):
        self.fail__when__contents_differ(ActResult(stdout_contents='expected',
                                                   stderr_contents='un-expected'),
                                         'expected')

    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals(ActResult(stdout_contents='un-expected',
                                                   stderr_contents='expected'),
                                         'expected')


class TestFileContentsFileRelTmpFORStdout(FileContentsFileRelTmp):
    def test_fail__when__comparison_file_does_not_exist(self):
        self.fail__when__comparison_file_does_not_exist()

    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        return ActResult(stdout_contents=contents_on_tested_channel,
                         stderr_contents=contents_on_other_channel)


class TestFileContentsFileRelTmpFORStderr(FileContentsFileRelTmp):
    def test_fail__when__comparison_file_does_not_exist(self):
        self.fail__when__comparison_file_does_not_exist()

    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        return ActResult(stderr_contents=contents_on_tested_channel,
                         stdout_contents=contents_on_other_channel)


class FileContentsHereDocFORStdout(FileContentsHereDoc):
    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        return ActResult(stdout_contents=contents_on_tested_channel,
                         stderr_contents=contents_on_other_channel)


class FileContentsHereDocFORStderr(FileContentsHereDoc):
    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        return ActResult(stderr_contents=contents_on_tested_channel,
                         stdout_contents=contents_on_other_channel)


class ReplacedEnvVars(TestWithParserBase):
    SOURCE_FILE_NAME = 'with-replaced-env-vars.txt'

    def __init__(self,
                 act_result_contents_setup: ActResultContentsSetup,
                 method_name):
        super().__init__(method_name)
        self._act_result_contents_setup = act_result_contents_setup

    def pass__when__contents_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            self._act_result_contents_setup,
            source_file_writer=WriteFileToHomeDir(self.SOURCE_FILE_NAME),
            source_should_contain_expected_value=True)
        self._run(
            new_source2(args('{replace_env_vars_option} {equals} {rel_home_option} {file}',
                             file=self.SOURCE_FILE_NAME)),
            arrangement(act_result_producer=act_result_producer),
            is_pass(),

        )

    def fail__when__contents_not_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            self._act_result_contents_setup,
            source_file_writer=WriteFileToHomeDir(self.SOURCE_FILE_NAME),
            source_should_contain_expected_value=False)
        self._run(
            new_source2(args('{replace_env_vars_option} {equals} {rel_home_option} {file}',
                             file=self.SOURCE_FILE_NAME)),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def pass__when__contents_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            self._act_result_contents_setup,
            source_file_writer=WriteFileToCurrentDir(self.SOURCE_FILE_NAME),
            source_should_contain_expected_value=True)
        self._run(
            new_source2(args('{replace_env_vars_option} {equals} {rel_cwd_option} {file}',
                             file=self.SOURCE_FILE_NAME)),
            arrangement(act_result_producer=act_result_producer),
            is_pass(),
        )

    def fail__when__contents_not_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            self._act_result_contents_setup,
            source_file_writer=WriteFileToCurrentDir(self.SOURCE_FILE_NAME),
            source_should_contain_expected_value=False)
        self._run(
            new_source2(args('{replace_env_vars_option} {equals} {rel_cwd_option} {file}',
                             file=self.SOURCE_FILE_NAME)),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestReplacedEnvVarsFORStdout(ReplacedEnvVars):
    def __init__(self, method_name):
        super().__init__(OutputContentsToStdout(), method_name)

    def test_pass__when__contents_equals__rel_home(self):
        self.pass__when__contents_equals__rel_home()

    def test_fail__when__contents_not_equals__rel_home(self):
        self.fail__when__contents_not_equals__rel_home()

    def test_pass__when__contents_equals__rel_cwd(self):
        self.pass__when__contents_equals__rel_cwd()

    def test_fail__when__contents_not_equals__rel_cwd(self):
        self.fail__when__contents_not_equals__rel_cwd()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()


class TestReplacedEnvVarsFORStderr(ReplacedEnvVars):
    def __init__(self, method_name):
        super().__init__(OutputContentsToStderr(), method_name)

    def test_pass__when__contents_equals__rel_home(self):
        self.pass__when__contents_equals__rel_home()

    def test_fail__when__contents_not_equals__rel_home(self):
        self.fail__when__contents_not_equals__rel_home()

    def test_pass__when__contents_equals__rel_cwd(self):
        self.pass__when__contents_equals__rel_cwd()

    def test_fail__when__contents_not_equals__rel_cwd(self):
        self.fail__when__contents_not_equals__rel_cwd()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()


def suite_for(instruction_configuration: TestConfiguration) -> unittest.TestSuite:
    def suite_for_option(option_configuration: RelativityOptionConfiguration) -> unittest.TestSuite:
        test_cases = [
            _ValidationErrorWhenComparisonFileDoesNotExist,
            _ValidationErrorWhenComparisonFileIsADirectory,
            _FaiWhenContentsDiffer,
            _PassWhenContentsEquals,
        ]
        return unittest.TestSuite([tc(instruction_configuration, option_configuration)
                                   for tc in test_cases])

    return unittest.TestSuite([
        suite_for_option(RelativityOptionConfigurationForRelHome())
    ])


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileContentsFileRelCwdFORStdout),
        unittest.makeSuite(TestFileContentsFileRelCwdFORStderr),

        unittest.makeSuite(FileContentsHereDocFORStdout),
        unittest.makeSuite(FileContentsHereDocFORStderr),

        unittest.makeSuite(TestReplacedEnvVarsFORStdout),
        unittest.makeSuite(TestReplacedEnvVarsFORStderr),

        unittest.makeSuite(TestFileContentsFileRelTmpFORStdout),
        unittest.makeSuite(TestFileContentsFileRelTmpFORStderr),
        suite_for(TestConfigurationForStdout()),
        suite_for(TestConfigurationForStderr()),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
