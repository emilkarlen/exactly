import unittest

from shellcheck_lib.execution import phase_step_simple as phase_step
from shellcheck_lib.execution.result import PartialResultStatus
from shellcheck_lib.test_case.phases.cleanup import PreviousPhase
from shellcheck_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr
from shellcheck_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from shellcheck_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_EDS_VALIDATION_STEPS__TWICE
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForNoFailure


class Test(TestCaseBase):
    def test_full_sequence(self):
        self._check(
                Arrangement(TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr()),
                Expectation(PartialResultStatus.PASS,
                            ExpectedFailureForNoFailure(),
                            PRE_EDS_VALIDATION_STEPS__TWICE +
                            [phase_step.SETUP__MAIN,
                             phase_step.SETUP__MAIN,
                             phase_step.SETUP__VALIDATE_POST_SETUP,
                             phase_step.SETUP__VALIDATE_POST_SETUP,
                             phase_step.ACT__VALIDATE_POST_SETUP,
                             phase_step.ACT__VALIDATE_POST_SETUP,
                             phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                             phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                             phase_step.ASSERT__VALIDATE_POST_SETUP,
                             phase_step.ASSERT__VALIDATE_POST_SETUP,
                             phase_step.ACT__MAIN,
                             phase_step.ACT__MAIN,
                             phase_step.ACT__SCRIPT_VALIDATE,
                             phase_step.ACT__SCRIPT_EXECUTE,
                             phase_step.BEFORE_ASSERT__MAIN,
                             phase_step.BEFORE_ASSERT__MAIN,
                             phase_step.ASSERT__MAIN,
                             phase_step.ASSERT__MAIN,
                             (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                             (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                             ],
                            True))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
