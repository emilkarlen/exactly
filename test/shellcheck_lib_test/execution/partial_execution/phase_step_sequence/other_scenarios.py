import unittest

from shellcheck_lib.execution import phase_step_simple as phase_step
from shellcheck_lib.execution.result import PartialResultStatus
from shellcheck_lib.test_case.phases.cleanup import PreviousPhase
from shellcheck_lib.test_case.phases.result import pfh
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.test_case.phases.result import svh
from shellcheck_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr
from shellcheck_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from shellcheck_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_EDS_VALIDATION_STEPS__TWICE
from shellcheck_lib_test.execution.test_resources.instruction_test_resources import do_raise, do_return
from shellcheck_lib_test.execution.test_resources.test_actions import validate_action_that_returns, \
    validate_action_that_raises, execute_action_that_raises
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForInstructionFailure, \
    ExpectedFailureForPhaseFailure


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
                            PRE_EDS_VALIDATION_STEPS__TWICE +
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
                            PRE_EDS_VALIDATION_STEPS__TWICE +
                            [phase_step.SETUP__MAIN,
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             ],
                            True))

    def test_hard_error_in_act_script_generate(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.ACT,
                 test.act_phase_instruction_that(
                         main=do_return(sh.new_sh_hard_error('hard error msg from act'))))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ACT__MAIN,
                                    test_case.the_extra(PartialPhase.ACT)[0].first_line,
                                    'hard error msg from act'),
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
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             ],
                            True))

    def test_implementation_error_in_act_script_generate(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.ACT,
                 test.act_phase_instruction_that(
                         main=do_raise(test.ImplementationErrorTestException())))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.ACT__MAIN,
                                    test_case.the_extra(PartialPhase.ACT)[0].first_line,
                                    test.ImplementationErrorTestException),
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
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             ],
                            True))

    def test_validation_error_in_act_script_validate(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr()
        self._check(
                Arrangement(test_case,
                            validate_test_action=validate_action_that_returns(
                                    svh.new_svh_validation_error('error message from validate'))),
                Expectation(PartialResultStatus.VALIDATE,
                            ExpectedFailureForPhaseFailure.new_with_message(
                                    phase_step.ACT__SCRIPT_VALIDATE,
                                    'error message from validate'),
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
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             ],
                            True))

    def test_hard_error_in_act_script_validate(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr()
        self._check(
                Arrangement(test_case,
                            validate_test_action=validate_action_that_returns(
                                    svh.new_svh_hard_error('error message from validate'))),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForPhaseFailure.new_with_message(
                                    phase_step.ACT__SCRIPT_VALIDATE,
                                    'error message from validate'),
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
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             ],
                            True))

    def test_implementation_error_in_act_script_validate(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr()
        self._check(
                Arrangement(test_case,
                            validate_test_action=validate_action_that_raises(
                                    test.ImplementationErrorTestException())),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForPhaseFailure.new_with_exception(
                                    phase_step.ACT__SCRIPT_VALIDATE,
                                    test.ImplementationErrorTestException),
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
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                             ],
                            True))

    def test_implementation_error_in_act_script_execute(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr()
        self._check(
                Arrangement(test_case,
                            execute_test_action=execute_action_that_raises(
                                    test.ImplementationErrorTestException())),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForPhaseFailure.new_with_exception(
                                    phase_step.ACT__SCRIPT_EXECUTE,
                                    test.ImplementationErrorTestException),
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


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
