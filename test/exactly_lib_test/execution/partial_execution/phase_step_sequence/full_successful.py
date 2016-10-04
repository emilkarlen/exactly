import unittest

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.result import PartialResultStatus
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_EDS_VALIDATION_STEPS__TWICE
from exactly_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForNoFailure


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


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
                         phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                         phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                         phase_step.ASSERT__VALIDATE_POST_SETUP,
                         phase_step.ASSERT__VALIDATE_POST_SETUP,

                         phase_step.ACT__PREPARE,
                         phase_step.ACT__EXECUTE,

                         phase_step.BEFORE_ASSERT__MAIN,
                         phase_step.BEFORE_ASSERT__MAIN,
                         phase_step.ASSERT__MAIN,
                         phase_step.ASSERT__MAIN,
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         ],
                        True))
