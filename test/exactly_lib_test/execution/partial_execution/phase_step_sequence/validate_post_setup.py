import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step_simple as phase_step
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.execution.partial_execution.test_resources.recording import validate_post_setup_utils as utils
from exactly_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_EDS_VALIDATION_STEPS__TWICE
from exactly_lib_test.execution.test_resources.instruction_test_resources import do_raise, do_return


def suite() -> unittest.TextTestRunner:
    ret_val = unittest.TestSuite()
    ret_val.addTests(utils.suite_for(conf)
                     for conf in _instruction_validation_invocations())
    return ret_val


class SetupConfig(utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.SETUP,
                         phase_step.SETUP__VALIDATE_POST_SETUP,
                         expected_steps=
                         PRE_EDS_VALIDATION_STEPS__TWICE + [
                             phase_step.SETUP__MAIN,
                             phase_step.SETUP__MAIN,
                             phase_step.SETUP__VALIDATE_POST_SETUP,
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                         ])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.setup_phase_instruction_that(
            validate_post_setup=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.setup_phase_instruction_that(validate_post_setup=do_raise(exception))


class BeforeAssertConfig(utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.BEFORE_ASSERT,
                         phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                         expected_steps=
                         PRE_EDS_VALIDATION_STEPS__TWICE + [
                             phase_step.SETUP__MAIN,
                             phase_step.SETUP__MAIN,
                             phase_step.SETUP__VALIDATE_POST_SETUP,
                             phase_step.SETUP__VALIDATE_POST_SETUP,
                             phase_step.ACT__VALIDATE_POST_SETUP,
                             phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                         ])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.before_assert_phase_instruction_that(
            validate_post_setup=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.before_assert_phase_instruction_that(validate_post_setup=do_raise(exception))


class AssertConfig(utils.Configuration):
    def __init__(self):
        super().__init__(PartialPhase.ASSERT,
                         phase_step.ASSERT__VALIDATE_POST_SETUP,
                         expected_steps=
                         PRE_EDS_VALIDATION_STEPS__TWICE + [
                             phase_step.SETUP__MAIN,
                             phase_step.SETUP__MAIN,
                             phase_step.SETUP__VALIDATE_POST_SETUP,
                             phase_step.SETUP__VALIDATE_POST_SETUP,
                             phase_step.ACT__VALIDATE_POST_SETUP,
                             phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                             phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                             phase_step.ASSERT__VALIDATE_POST_SETUP,
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                         ])

    def instruction_that_returns(self, return_value: svh.SuccessOrValidationErrorOrHardError) -> TestCaseInstruction:
        return test.assert_phase_instruction_that(
            validate_post_setup=do_return(return_value))

    def instruction_that_raises(self, exception: Exception) -> TestCaseInstruction:
        return test.assert_phase_instruction_that(validate_post_setup=do_raise(exception))


def _instruction_validation_invocations() -> list:
    return [
        SetupConfig(),
        BeforeAssertConfig(),
        AssertConfig(),
    ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
