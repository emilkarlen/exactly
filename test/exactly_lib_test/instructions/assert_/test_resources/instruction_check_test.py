"""
Test of test-infrastructure: instruction_check.
"""
import unittest

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.execution.test_resources.instruction_test_resources import \
    assert_phase_instruction_that
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, is_pass, \
    Expectation
from exactly_lib_test.instructions.test_resources import test_of_test_framework_utils as test_misc


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCases))
    return ret_val


class TestCases(instruction_check.TestCaseBase):
    def test_successful_flow(self):
        self._check(
            test_misc.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
            test_misc.single_line_source(),
            arrangement(),
            is_pass())

    def test_fail_due_to_unexpected_result_from_pre_validation(self):
        with self.assertRaises(test_misc.TestError):
            self._check(test_misc.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                        test_misc.single_line_source(),
                        arrangement(),
                        Expectation(validation_pre_sds=test_misc.raises_test_error()),
                        )

    def test_fail_due_to_unexpected_result_from_post_validation(self):
        with self.assertRaises(test_misc.TestError):
            self._check(test_misc.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                        test_misc.single_line_source(),
                        arrangement(),
                        Expectation(validation_post_sds=test_misc.raises_test_error()),
                        )

    def test_fail_due_to_unexpected_result_from_main(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                test_misc.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                test_misc.single_line_source(),
                arrangement(),
                Expectation(main_result=test_misc.raises_test_error()),
            )

    def test_fail_due_to_fail_of_side_effects_on_files(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                test_misc.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                test_misc.single_line_source(),
                arrangement(),
                Expectation(main_side_effects_on_files=test_misc.raises_test_error()),
            )

    def test_that_cwd_for_main_and_post_validation_is_test_root(self):
        self._check(
            test_misc.ParserThatGives(InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot()),
            test_misc.single_line_source(),
            arrangement(),
            is_pass())

    def test_fail_due_to_side_effects_check(self):
        with self.assertRaises(test_misc.TestError):
            self._check(
                test_misc.ParserThatGives(_SUCCESSFUL_INSTRUCTION),
                test_misc.single_line_source(),
                arrangement(),
                Expectation(side_effects_check=test_misc.raises_test_error()),
            )


_SUCCESSFUL_INSTRUCTION = assert_phase_instruction_that()


class InstructionThatRaisesTestErrorIfCwdIsIsNotTestRoot(AssertPhaseInstruction):
    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        test_misc.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return svh.new_svh_success()

    def main(self, environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        test_misc.raise_test_error_if_cwd_is_not_test_root(environment.sds)
        return pfh.new_pfh_pass()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
