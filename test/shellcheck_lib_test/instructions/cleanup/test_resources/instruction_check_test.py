"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction, PreviousPhase
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib_test.execution.test_resources.instruction_test_resources import \
    cleanup_phase_instruction_that
from shellcheck_lib_test.instructions.cleanup.test_resources import instruction_check as sut
from shellcheck_lib_test.instructions.test_resources import test_of_test_framework_utils as test_misc


class TestCases(sut.TestCaseBase):
    def test_successful_flow(self):
        self._check(
                test_misc.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                test_misc.single_line_source(),
                sut.Arrangement(),
                sut.Expectation(),
        )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                    test_misc.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                    test_misc.single_line_source(),
                    sut.Arrangement(),
                    sut.Expectation(main_result=test_misc.ShRaisesTestError()),
            )

    def test_fail_due_to_unexpected_result_from_validate_pre_eds(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                    test_misc.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                    test_misc.single_line_source(),
                    sut.Arrangement(),
                    sut.Expectation(validate_pre_eds_result=test_misc.SvhRaisesTestError()),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                    test_misc.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                    test_misc.single_line_source(),
                    sut.Arrangement(),
                    sut.Expectation(main_side_effects_on_files=test_misc.EdsContentsRaisesTestError()),
            )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(test_misc.ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot()),
                    test_misc.single_line_source(),
                    sut.Arrangement(),
                    sut.Expectation(),
                    )

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(test_misc.TestError):
            self._check(test_misc.ParserThatGives(SUCCESSFUL_INSTRUCTION),
                        test_misc.single_line_source(),
                        sut.Arrangement(),
                        sut.Expectation(side_effects_check=test_misc.SideEffectsCheckThatRaisesTestError()),
                        )


SUCCESSFUL_INSTRUCTION = cleanup_phase_instruction_that()


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(CleanupPhaseInstruction):
    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             previous_phase: PreviousPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        test_misc.raise_test_error_if_cwd_is_not_test_root(environment.eds)
        return sh.new_sh_success()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
