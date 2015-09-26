"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib_test.execution.full_execution.util.instruction_test_resources import \
    CleanupPhaseInstructionThatReturns
from shellcheck_lib_test.instructions.cleanup.test_resources import instruction_check
from shellcheck_lib_test.instructions.test_resources import test_of_test_framework_utils as test_misc


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

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                instruction_check.Flow(test_misc.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                                       expected_main_result=test_misc.ShRaisesTestError()),
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


SUCCESSFUL_INSTRUCTION = CleanupPhaseInstructionThatReturns(sh.new_sh_success())


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(CleanupPhaseInstruction):
    def main(self, environment: GlobalEnvironmentForPostEdsPhase, os_services: OsServices) -> pfh.PassOrFailOrHardError:
        test_misc.raise_test_error_if_cwd_is_not_test_root(environment.eds)
        return pfh.new_pfh_pass()
