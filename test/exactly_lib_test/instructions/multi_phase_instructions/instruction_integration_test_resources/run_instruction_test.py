import unittest

from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import \
    ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.instructions.test_resources.run_instruction_utils import source_for_interpreting
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.parse import single_line_source
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe


class Configuration(ConfigurationBase):
    def expect_failure_because_specified_file_under_sds_is_missing(self):
        raise NotImplementedError()


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.conf))


class TestSuccessfulExecution(TestCaseBase):
    def runTest(self):
        self.conf.run_test(self,
                           single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(0)')),
                           self.conf.arrangement(),
                           self.conf.expect_success(),
                           )


class TestFailingExecution(TestCaseBase):
    def runTest(self):
        self.conf.run_test(self,
                           single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(1)')),
                           self.conf.arrangement(),
                           self.conf.expect_failure_of_main(),
                           )


class TestFailingValidationOfAbsolutePath(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
            self,
            single_line_source('/absolute/path/to/program/that/does/not/exist'),
            self.conf.arrangement(),
            self.conf.expect_failing_validation_pre_sds(),
        )


class TestFailingValidationOfRelHomePath(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
            self,
            source_for_interpreting(file_ref_texts.REL_HOME_OPTION, 'non-existing-file.py'),
            self.conf.arrangement(),
            self.conf.expect_failing_validation_pre_sds(),
        )


class TestFailingValidationOfRelTmpPath(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
            self,
            source_for_interpreting(file_ref_texts.REL_TMP_OPTION, 'non-existing-file.py'),
            self.conf.arrangement(),
            self.conf.expect_failure_because_specified_file_under_sds_is_missing(),
        )


class TestSuccessfulValidation(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
            self,
            source_for_interpreting(file_ref_texts.REL_TMP_OPTION, 'existing-file.py'),
            self.conf.arrangement(sds_contents_before_main=sds_populator.tmp_user_dir_contents(
                DirContents([empty_file('existing-file.py')]))),
            self.conf.expect_success(),
        )


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf,
                           [
                               TestSuccessfulExecution,
                               TestFailingExecution,
                               TestFailingValidationOfAbsolutePath,
                               TestFailingValidationOfRelHomePath,
                               TestFailingValidationOfRelTmpPath,
                               TestSuccessfulValidation,
                           ])
