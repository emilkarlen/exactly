import unittest
from abc import ABC

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_documentation_instance
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_resources.files.file_utils import tmp_file_containing
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe


class Configuration(ConfigurationBase, ABC):
    def expectation_for_non_zero_exitcode(self):
        raise NotImplementedError()

    def expectation_for_zero_exitcode(self):
        raise NotImplementedError()


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


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf


class TestParseFailsWhenThereAreNoArguments(TestCaseBase):
    def runTest(self):
        for source in equivalent_source_variants(self, '   '):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                self.conf.parser().parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero(TestCaseBase):
    def runTest(self):
        script_that_exists_with_status_0 = """
import sys
sys.exit(0)
"""
        with tmp_file_containing(script_that_exists_with_status_0,
                                 suffix='.py') as script_file_path:
            instruction_argument = py_exe.shell_command_line_for_interpreting(script_file_path)
            self.conf.run_single_line_test_with_source_variants_and_source_check(
                self,
                instruction_argument,
                self.conf.arrangement(),
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
            self.conf.run_single_line_test_with_source_variants_and_source_check(
                self,
                instruction_argument,
                self.conf.arrangement(),
                self.conf.expectation_for_non_zero_exitcode(),
            )
