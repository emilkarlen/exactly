import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.instructions.test_resources.check_description import suite_for_description_instance
from exactly_lib_test.test_resources import python_program_execution as py_exe
from exactly_lib_test.test_resources.file_utils import tmp_file_containing
from exactly_lib_test.test_resources.parse import new_source2


class Configuration(ConfigurationBase):
    def expectation_for_non_zero_exitcode(self) -> Expectation:
        raise NotImplementedError()

    def expectation_for_zero_exitcode(self) -> Expectation:
        raise NotImplementedError()


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf


class TestParseFailsWhenThereAreNoArguments(TestCaseBase):
    def runTest(self):
        source = new_source2('   ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.conf.parser().apply(source)


class TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero(TestCaseBase):
    def runTest(self):
        script_that_exists_with_status_0 = """
import sys
sys.exit(0)
"""
        with tmp_file_containing(script_that_exists_with_status_0,
                                 suffix='.py') as script_file_path:
            self.conf.run_test(
                    self,
                    new_source2(py_exe.shell_command_line_for_interpreting(script_file_path)),
                    self.conf.empty_arrangement(),
                    self.conf.expectation_for_zero_exitcode(),
            )


class TestInstructionIsHardErrorWhenExitStatusFromCommandIsNonZero(TestCaseBase):
    def runTest(self):
        script_that_exists_with_status_0 = """
import sys
sys.exit(1)
"""
        with tmp_file_containing(script_that_exists_with_status_0,
                                 suffix='.py') as script_file_path:
            self.conf.run_test(
                    self,
                    new_source2(py_exe.command_line_for_interpreting(script_file_path)),
                    self.conf.empty_arrangement(),
                    self.conf.expectation_for_non_zero_exitcode(),
            )


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_description_instance(configuration.description()),
        suite_for_cases(configuration,
                        [
                            TestParseFailsWhenThereAreNoArguments,
                            TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero,
                            TestInstructionIsHardErrorWhenExitStatusFromCommandIsNonZero,
                        ])
    ])
