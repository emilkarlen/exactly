import unittest

from exactly_lib.instructions.assert_ import stdout_stderr as sut
from exactly_lib.instructions.assert_.utils.file_contents.parsing import EQUALS_ARGUMENT
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.assert_.stdout_stderr.test_resources import TestWithParserBase, \
    TestConfigurationForStdout, TestConfigurationForStderr
from exactly_lib_test.instructions.assert_.test_resources.contents_resources import \
    ActResultProducerForContentsWithAllReplacedEnvVars, \
    OutputContentsToStdout, WriteFileToHomeDir, ActResultContentsSetup, OutputContentsToStderr, WriteFileToCurrentDir
from exactly_lib_test.instructions.assert_.test_resources.file_contents import equals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    args
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, Expectation, is_pass
from exactly_lib_test.instructions.test_resources.arrangements import ActResultProducerFromActResult
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.parse import new_source2, argument_list_source


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


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(FileContentsHereDocFORStdout),
        unittest.makeSuite(FileContentsHereDocFORStderr),

        unittest.makeSuite(TestReplacedEnvVarsFORStdout),
        unittest.makeSuite(TestReplacedEnvVarsFORStderr),

        equals.suite_for(TestConfigurationForStdout()),
        equals.suite_for(TestConfigurationForStderr()),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
