"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser

from shellcheck_lib.general import line_source

from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.sections.setup import SetupPhaseInstruction
from shellcheck_lib_test.execution.full_execution.util.instruction_test_resources import \
    SetupPhaseInstructionThatReturns
from shellcheck_lib_test.instructions.setup.test_resources import instruction_check
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.utils import SingleInstructionParserSource
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources import sh_check


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()


class TestCases(instruction_check.TestCaseBase):
    def test_successful_flow(self):
        self._check(instruction_check.Flow(ParserThatGivesAnInstructionThatJustSucceeds()),
                    single_line_source())

    @unittest.expectedFailure
    def test_fail_due_to_unexpected_pre_validation_result(self):
        self._check(instruction_check.Flow(ParserThatGivesAnInstructionThatJustSucceeds(),
                                           expected_pre_validation_result=svh_check.StatusIs(
                                               svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR)),
                    single_line_source())

    @unittest.expectedFailure
    def test_fail_due_to_unexpected_pre_validation_result(self):
        self._check(instruction_check.Flow(ParserThatGivesAnInstructionThatJustSucceeds(),
                                           expected_main_result=sh_check.IsHardError()),
                    single_line_source())


def single_line_source() -> SingleInstructionParserSource:
    return utils.new_source('instruction name', 'instruction arguments')


class ParserThatGivesAnInstructionThatJustSucceeds(SingleInstructionParser):
    def apply(self, source: line_source.LineSequenceBuilder, instruction_argument: str) -> SetupPhaseInstruction:
        return SetupPhaseInstructionThatReturns(svh.new_svh_success(),
                                                sh.new_sh_success(),
                                                svh.new_svh_success())
