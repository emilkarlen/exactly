"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.test_resources.instruction_test_resources import \
    assert_phase_instruction_that
from shellcheck_lib_test.instructions.assert_phase.test_resources import instruction_check
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Arrangement, is_pass, \
    Expectation
from shellcheck_lib_test.instructions.test_resources import test_of_test_framework_utils as test_misc


class TestCases(instruction_check.TestCaseBase):
    def test_successful_flow(self):
        self._check(
                test_misc.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                test_misc.single_line_source(),
                Arrangement(),
                is_pass())

    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(test_misc.TestError):
            self._check(test_misc.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                        test_misc.single_line_source(),
                        Arrangement(),
                        Expectation(validation_pre_eds=test_misc.SvhRaisesTestError()),
                        )

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(test_misc.TestError):
            self._check(test_misc.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                        test_misc.single_line_source(),
                        Arrangement(),
                        Expectation(validation_post_eds=test_misc.SvhRaisesTestError()),
                        )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                    test_misc.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                    test_misc.single_line_source(),
                    Arrangement(),
                    Expectation(main_result=test_misc.PfhRaisesTestError()),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                    test_misc.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                    test_misc.single_line_source(),
                    Arrangement(),
                    Expectation(main_side_effects_on_files=test_misc.EdsContentsRaisesTestError()),
            )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(
                test_misc.ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot()),
                test_misc.single_line_source(),
                Arrangement(),
                is_pass())

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                    test_misc.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                    test_misc.single_line_source(),
                    Arrangement(),
                    Expectation(side_effects_check=test_misc.SideEffectsCheckThatRaisesTestError()),
            )


_SUCCESSFUL_INSTRUCTION = assert_phase_instruction_that()


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(AssertPhaseInstruction):
    def validate_post_setup(self,
                            environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        test_misc.raise_test_error_if_cwd_is_not_test_root(environment.eds)
        return svh.new_svh_success()

    def main(self, environment: GlobalEnvironmentForPostEdsPhase, os_services: OsServices) -> pfh.PassOrFailOrHardError:
        test_misc.raise_test_error_if_cwd_is_not_test_root(environment.eds)
        return pfh.new_pfh_pass()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


if __name__ == '__main__':
    unittest.main()
