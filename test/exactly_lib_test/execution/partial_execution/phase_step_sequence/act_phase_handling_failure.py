import unittest

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.result import PartialResultStatus
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList, \
    TestCaseGeneratorForExecutionRecording
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import \
    PRE_EDS_VALIDATION_STEPS__ONCE
from exactly_lib_test.execution.test_resources.test_actions import execute_action_that_raises, \
    execute_action_that_returns_hard_error_with_message, \
    prepare_action_that_returns_hard_error_with_message
from exactly_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForPhaseFailure


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class Test(TestCaseBase):
    def test_hard_error_in_act_program_prepare(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        prepare_test_action=prepare_action_that_returns_hard_error_with_message(
                            'error in act/prepare')),
            Expectation(PartialResultStatus.HARD_ERROR,
                        ExpectedFailureForPhaseFailure.new_with_message(
                            phase_step.ACT__PREPARE,
                            'error in act/prepare'),
                        PRE_EDS_VALIDATION_STEPS__ONCE +
                        [phase_step.SETUP__MAIN,

                         phase_step.SETUP__VALIDATE_POST_SETUP,
                         phase_step.ACT__VALIDATE_POST_SETUP,
                         phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                         phase_step.ASSERT__VALIDATE_POST_SETUP,

                         phase_step.ACT__PREPARE,

                         (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                         ],
                        True))

    def test_implementation_error_in_act_program_prepare(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        prepare_test_action=execute_action_that_raises(
                            test.ImplementationErrorTestException())),
            Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                        ExpectedFailureForPhaseFailure.new_with_exception(
                            phase_step.ACT__PREPARE,
                            test.ImplementationErrorTestException),
                        PRE_EDS_VALIDATION_STEPS__ONCE +
                        [phase_step.SETUP__MAIN,

                         phase_step.SETUP__VALIDATE_POST_SETUP,
                         phase_step.ACT__VALIDATE_POST_SETUP,
                         phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                         phase_step.ASSERT__VALIDATE_POST_SETUP,

                         phase_step.ACT__PREPARE,

                         (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                         ],
                        True))

    def test_hard_error_in_act_program_execute(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        execute_test_action=execute_action_that_returns_hard_error_with_message(
                            'error in execute')),
            Expectation(PartialResultStatus.HARD_ERROR,
                        ExpectedFailureForPhaseFailure.new_with_message(
                            phase_step.ACT__EXECUTE,
                            'error in execute'),
                        PRE_EDS_VALIDATION_STEPS__ONCE +
                        [phase_step.SETUP__MAIN,

                         phase_step.SETUP__VALIDATE_POST_SETUP,
                         phase_step.ACT__VALIDATE_POST_SETUP,
                         phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                         phase_step.ASSERT__VALIDATE_POST_SETUP,

                         phase_step.ACT__PREPARE,
                         phase_step.ACT__EXECUTE,

                         (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                         ],
                        True))

    def test_implementation_error_in_act_program_execute(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        execute_test_action=execute_action_that_raises(
                            test.ImplementationErrorTestException())),
            Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                        ExpectedFailureForPhaseFailure.new_with_exception(
                            phase_step.ACT__EXECUTE,
                            test.ImplementationErrorTestException),
                        PRE_EDS_VALIDATION_STEPS__ONCE +
                        [phase_step.SETUP__MAIN,

                         phase_step.SETUP__VALIDATE_POST_SETUP,
                         phase_step.ACT__VALIDATE_POST_SETUP,
                         phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                         phase_step.ASSERT__VALIDATE_POST_SETUP,

                         phase_step.ACT__PREPARE,
                         phase_step.ACT__EXECUTE,

                         (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                         ],
                        True))


def _single_successful_instruction_in_each_phase() -> TestCaseGeneratorForExecutionRecording:
    return TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList()
