import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step_simple as phase_step
from exactly_lib.execution.result import PartialResultStatus
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_SDS_VALIDATION_STEPS__TWICE
from exactly_lib_test.execution.test_resources.instruction_test_resources import do_raise, do_return
from exactly_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForInstructionFailure


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class Test(TestCaseBase):
    def test_hard_error_in_setup_main_step(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.SETUP,
                 test.setup_phase_instruction_that(
                     main=do_return(sh.new_sh_hard_error('hard error msg from setup'))))
        self._check(
            Arrangement(test_case),
            Expectation(PartialResultStatus.HARD_ERROR,
                        ExpectedFailureForInstructionFailure.new_with_message(
                            phase_step.SETUP__MAIN,
                            test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                            'hard error msg from setup'),
                        PRE_SDS_VALIDATION_STEPS__TWICE +
                        [phase_step.SETUP__MAIN,
                         (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                         (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                         ],
                        True))

    def test_implementation_error_in_setup_main_step(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.SETUP,
                 test.setup_phase_instruction_that(
                     main=do_raise(test.ImplementationErrorTestException())))
        self._check(
            Arrangement(test_case),
            Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                        ExpectedFailureForInstructionFailure.new_with_exception(
                            phase_step.SETUP__MAIN,
                            test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                            test.ImplementationErrorTestException),
                        PRE_SDS_VALIDATION_STEPS__TWICE +
                        [phase_step.SETUP__MAIN,
                         (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                         (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                         ],
                        True))

    def test_hard_error_in_before_assert_main_step(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.BEFORE_ASSERT,
                 test.before_assert_phase_instruction_that(
                     main=do_return(sh.new_sh_hard_error('hard error msg'))))
        self._check(
            Arrangement(test_case),
            Expectation(PartialResultStatus.HARD_ERROR,
                        ExpectedFailureForInstructionFailure.new_with_message(
                            phase_step.BEFORE_ASSERT__MAIN,
                            test_case.the_extra(PartialPhase.BEFORE_ASSERT)[0].first_line,
                            'hard error msg'),
                        PRE_SDS_VALIDATION_STEPS__TWICE +
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
                         (phase_step.CLEANUP__MAIN, PreviousPhase.BEFORE_ASSERT),
                         (phase_step.CLEANUP__MAIN, PreviousPhase.BEFORE_ASSERT),
                         ],
                        True))

    def test_implementation_error_in_before_assert_main_step(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.BEFORE_ASSERT,
                 test.before_assert_phase_instruction_that(
                     main=test.do_raise(test.ImplementationErrorTestException())))
        self._check(
            Arrangement(test_case),
            Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                        ExpectedFailureForInstructionFailure.new_with_exception(
                            phase_step.BEFORE_ASSERT__MAIN,
                            test_case.the_extra(PartialPhase.BEFORE_ASSERT)[0].first_line,
                            test.ImplementationErrorTestException),
                        PRE_SDS_VALIDATION_STEPS__TWICE +
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
                         (phase_step.CLEANUP__MAIN, PreviousPhase.BEFORE_ASSERT),
                         (phase_step.CLEANUP__MAIN, PreviousPhase.BEFORE_ASSERT),
                         ],
                        True))

    def test_fail_in_assert_main_step(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that(
                     main=do_return(pfh.new_pfh_fail('fail msg from ASSERT'))))
        self._check(
            Arrangement(test_case),
            Expectation(PartialResultStatus.FAIL,
                        ExpectedFailureForInstructionFailure.new_with_message(
                            phase_step.ASSERT__MAIN,
                            test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                            'fail msg from ASSERT'),
                        PRE_SDS_VALIDATION_STEPS__TWICE +
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
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         ],
                        True))

    def test_hard_error_in_assert_main_step(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that(
                     main=do_return(pfh.new_pfh_hard_error('hard error msg from ASSERT'))))
        self._check(
            Arrangement(test_case),
            Expectation(PartialResultStatus.HARD_ERROR,
                        ExpectedFailureForInstructionFailure.new_with_message(
                            phase_step.ASSERT__MAIN,
                            test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                            'hard error msg from ASSERT'),
                        PRE_SDS_VALIDATION_STEPS__TWICE +
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
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         ],
                        True))

    def test_implementation_error_in_assert_main_step(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that(
                     main=test.do_raise(test.ImplementationErrorTestException())))
        self._check(
            Arrangement(test_case),
            Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                        ExpectedFailureForInstructionFailure.new_with_exception(
                            phase_step.ASSERT__MAIN,
                            test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                            test.ImplementationErrorTestException),
                        PRE_SDS_VALIDATION_STEPS__TWICE +
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
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         ],
                        True))

    def test_hard_error_in_cleanup_main_step(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.CLEANUP,
                 test.cleanup_phase_instruction_that(
                     main=test.do_return(sh.new_sh_hard_error('hard error msg from CLEANUP'))))
        self._check(
            Arrangement(test_case),
            Expectation(PartialResultStatus.HARD_ERROR,
                        ExpectedFailureForInstructionFailure.new_with_message(
                            phase_step.CLEANUP__MAIN,
                            test_case.the_extra(PartialPhase.CLEANUP)[0].first_line,
                            'hard error msg from CLEANUP'),
                        PRE_SDS_VALIDATION_STEPS__TWICE +
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
                         ],
                        True))

    def test_implementation_error_in_cleanup_main_step(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.CLEANUP,
                 test.cleanup_phase_instruction_that(
                     main=test.do_raise(test.ImplementationErrorTestException())))
        self._check(
            Arrangement(test_case),
            Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                        ExpectedFailureForInstructionFailure.new_with_exception(
                            phase_step.CLEANUP__MAIN,
                            test_case.the_extra(PartialPhase.CLEANUP)[0].first_line,
                            test.ImplementationErrorTestException),
                        PRE_SDS_VALIDATION_STEPS__TWICE +
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
                         ],
                        True))
