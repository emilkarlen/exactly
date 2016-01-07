import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource, SingleInstructionParser
from shellcheck_lib.instructions.assert_phase import shell as sut
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import arrangement, Expectation, \
    check
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources.arrangement import ArrangementPostAct
from shellcheck_lib_test.instructions.test_resources.utils import new_source2
from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.test_resources.file_utils import tmp_file_containing


class Configuration:
    def run_test(self,
                 put: unittest.TestCase,
                 source: SingleInstructionParserSource,
                 arrangement,
                 expectation):
        check(put, self.parser(), source, arrangement, expectation)

    def parser(self) -> SingleInstructionParser:
        return sut.parser()

    def empty_arrangement(self) -> ArrangementPostAct:
        return arrangement()

    def expectation_of_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=pfh_check.is_fail())

    def expectation_of_zero_exitcode(self) -> Expectation:
        return Expectation()


class TestParseFailsWhenThereAreNoArguments(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf

    def runTest(self):
        source = new_source2('   ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.conf.parser().apply(source)


class TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf

    def runTest(self):
        script_that_exists_with_status_0 = """
import sys
sys.exit(0)
"""
        with tmp_file_containing(script_that_exists_with_status_0,
                                 suffix='.py') as script_file_path:
            self.conf.run_test(
                    self,
                    new_source2(py_exe.command_line_for_interpreting(script_file_path)),
                    self.conf.empty_arrangement(),
                    self.conf.expectation_of_zero_exitcode(),
            )


class TestInstructionIsHardErrorWhenExitStatusFromCommandIsNonZero(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf

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
                    self.conf.expectation_of_non_zero_exitcode(),
            )


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTests([TestParseFailsWhenThereAreNoArguments(configuration),
                      TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero(configuration),
                      TestInstructionIsHardErrorWhenExitStatusFromCommandIsNonZero(configuration),
                      ])
    return ret_val
