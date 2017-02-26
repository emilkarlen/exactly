import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.instructions.test_resources.check_description import suite_for_documentation_instance
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, \
    check_equivalent_source_variants
from exactly_lib_test.test_resources.file_utils import tmp_file_containing
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe


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
        for source in equivalent_source_variants(self, '   '):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                self.conf.parser().parse(source)


class TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero(TestCaseBase):
    def runTest(self):
        script_that_exists_with_status_0 = """
import sys
sys.exit(0)
"""
        with tmp_file_containing(script_that_exists_with_status_0,
                                 suffix='.py') as script_file_path:
            instruction_argument = py_exe.shell_command_line_for_interpreting(script_file_path)
            for source in check_equivalent_source_variants(self, instruction_argument):
                self.conf.run_test(
                    self,
                    source,
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
            instruction_argument = py_exe.command_line_for_interpreting(script_file_path)
            for source in check_equivalent_source_variants(self, instruction_argument):
                self.conf.run_test(
                    self,
                    source,
                    self.conf.empty_arrangement(),
                    self.conf.expectation_for_non_zero_exitcode(),
                )


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_documentation_instance(configuration.documentation()),
        suite_for_cases(configuration,
                        [
                            TestParseFailsWhenThereAreNoArguments,
                            TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero,
                            TestInstructionIsHardErrorWhenExitStatusFromCommandIsNonZero,
                        ])
    ])
