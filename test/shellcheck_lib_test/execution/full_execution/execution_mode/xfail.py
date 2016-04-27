import unittest

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution import phases
from exactly_lib.execution.execution_mode import ExecutionMode
from exactly_lib.execution.result import FullResultStatus
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from shellcheck_lib_test.execution.full_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr
from shellcheck_lib_test.execution.full_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_EDS_VALIDATION_STEPS__TWICE
from shellcheck_lib_test.execution.test_resources.instruction_test_resources import do_return
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForInstructionFailure, \
    ExpectedFailureForNoFailure


class Test(TestCaseBase):
    def test_with_assert_phase_that_fails(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL)) \
            .add(phases.ASSERT,
                 test.assert_phase_instruction_that(
                         main=test.do_return(pfh.new_pfh_fail('fail message'))))
        self._check(Arrangement(test_case),
                    Expectation(FullResultStatus.XFAIL,
                                ExpectedFailureForInstructionFailure.new_with_message(
                                        phase_step.ASSERT__MAIN,
                                        test_case.the_extra(phases.ASSERT)[0].first_line,
                                        'fail message'),
                                [phase_step.ANONYMOUS__MAIN,
                                 phase_step.ANONYMOUS__MAIN] +
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
                                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                                 ],
                                True))

    def test_with_assert_phase_that_passes(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.XPASS,
                            ExpectedFailureForNoFailure(),
                            [phase_step.ANONYMOUS__MAIN,
                             phase_step.ANONYMOUS__MAIN] +
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

    def test_with_anonymous_phase_with_hard_error(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL)) \
            .add(phases.ANONYMOUS,
                 test.anonymous_phase_instruction_that(do_return(sh.new_sh_hard_error('hard error msg'))))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ANONYMOUS__MAIN,
                                    test_case.the_extra(phases.ANONYMOUS)[1].first_line,
                                    'hard error msg'),
                            [phase_step.ANONYMOUS__MAIN],
                            False))

    def test_with_implementation_error(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL)) \
            .add(phases.CLEANUP,
                 test.cleanup_phase_instruction_that(
                         main=test.do_raise(test.ImplementationErrorTestException())))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.CLEANUP__MAIN,
                                    test_case.the_extra(phases.CLEANUP)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.ANONYMOUS__MAIN,
                             phase_step.ANONYMOUS__MAIN] +
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
                             ],
                            True))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
