"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase, \
    PhaseEnvironmentForInternalCommands
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case.instruction.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib_test.execution.full_execution.util.instruction_test_resources import \
    AssertPhaseInstructionThatReturns
from shellcheck_lib_test.instructions.assert_phase.test_resources import instruction_check
from shellcheck_lib_test.instructions.test_resources import misc as test_misc


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()


class TestCases(instruction_check.TestCaseBase):
    def test_successful_flow(self):
        self._check(
            instruction_check.Flow(test_misc.ParserThatGives(SUCCESSFUL_INSTRUCTION)),
            test_misc.single_line_source())

    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                instruction_check.Flow(test_misc.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_validation_result=test_misc.SvhRaisesTestError()),
                test_misc.single_line_source())

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                instruction_check.Flow(test_misc.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_main_result=test_misc.PfhRaisesTestError()),
                test_misc.single_line_source())

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                instruction_check.Flow(test_misc.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_main_side_effects_on_files=test_misc.EdsContentsRaisesTestError()),
                test_misc.single_line_source())

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(
            instruction_check.Flow(test_misc.ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot())),
            test_misc.single_line_source())


SUCCESSFUL_INSTRUCTION = AssertPhaseInstructionThatReturns(svh.new_svh_success(),
                                                           pfh.new_pfh_pass())


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(AssertPhaseInstruction):
    def validate(self, global_environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        test_misc.raise_test_error_if_cwd_is_not_test_root(global_environment.eds)
        return svh.new_svh_success()

    def main(self,
             global_environment: GlobalEnvironmentForPostEdsPhase,
             phase_environment: PhaseEnvironmentForInternalCommands) -> pfh.PassOrFailOrHardError:
        test_misc.raise_test_error_if_cwd_is_not_test_root(global_environment.eds)
        return pfh.new_pfh_pass()
