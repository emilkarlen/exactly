import unittest

from shellcheck_lib.instructions.utils import relative_path_options as options
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources.execute_utils import source_for_interpreting
from shellcheck_lib_test.instructions.test_resources.utils import single_line_source
from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.test_resources.file_structure import DirContents, empty_file


class Configuration(ConfigurationBase):
    def expect_failure_because_specified_file_under_eds_is_missing(self):
        raise NotImplementedError()


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf


class TestSuccessfulExecution(TestCaseBase):
    def runTest(self):
        self.conf.run_test(self,
                           single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(0)')),
                           self.conf.empty_arrangement(),
                           self.conf.expect_success(),
                           )


class TestFailingExecution(TestCaseBase):
    def runTest(self):
        self.conf.run_test(self,
                           single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(1)')),
                           self.conf.empty_arrangement(),
                           self.conf.expect_failure_of_main(),
                           )


class TestFailingValidationOfAbsolutePath(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
                self,
                single_line_source('/absolute/path/to/program/that/does/not/exist'),
                self.conf.empty_arrangement(),
                self.conf.expect_failing_validation_pre_eds(),
        )


class TestFailingValidationOfRelHomePath(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
                self,
                source_for_interpreting(options.REL_HOME_OPTION, 'non-existing-file.py'),
                self.conf.empty_arrangement(),
                self.conf.expect_failing_validation_pre_eds(),
        )


class TestFailingValidationOfRelTmpPath(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
                self,
                source_for_interpreting(options.REL_TMP_OPTION, 'non-existing-file.py'),
                self.conf.empty_arrangement(),
                self.conf.expect_failure_because_specified_file_under_eds_is_missing(),
        )


class TestSuccessfulValidation(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
                self,
                source_for_interpreting(options.REL_TMP_OPTION, 'existing-file.py'),
                self.conf.arrangement(eds_contents_before_main=eds_populator.tmp_user_dir_contents(
                        DirContents([empty_file('existing-file.py')]))),
                self.conf.expect_success(),
        )


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return unittest.TestSuite(
            tcc(conf) for tcc in [TestSuccessfulExecution,
                                  TestFailingExecution,
                                  TestFailingValidationOfAbsolutePath,
                                  TestFailingValidationOfRelHomePath,
                                  TestFailingValidationOfRelTmpPath,
                                  TestSuccessfulValidation])
