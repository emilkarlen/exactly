import unittest

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.result import ExecutionFailureStatus
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.result import pfh, sh
from exactly_lib_test.execution.partial_execution.test_resources import result_assertions as asrt_result
from exactly_lib_test.execution.partial_execution.test_resources.hard_error_ex import hard_error_ex
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_SDS_VALIDATION_STEPS__TWICE, \
    SYMBOL_VALIDATION_STEPS__TWICE
from exactly_lib_test.execution.test_resources.failure_info_check import ExpectedFailureForInstructionFailure
from exactly_lib_test.test_case.actor.test_resources.test_actions import \
    execute_action_that_returns_exit_code
from exactly_lib_test.test_resources.actions import do_return, do_raise


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSetupMainStep),
        unittest.makeSuite(TestBeforeAssertMainStep),
        unittest.makeSuite(TestAssertMainStep),
        unittest.makeSuite(TestCleanupMainStep),
    ])


class TestSetupMainStep(TestCaseBase):
    def test_hard_error(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.SETUP,
                 test.setup_phase_instruction_that(
                     main=do_return(sh.new_sh_hard_error__str('hard error msg from setup'))))
        self._check(
            Arrangement(test_case),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.HARD_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.SETUP__MAIN,
                        test_case.the_extra(PartialPhase.SETUP)[0].source,
                        'hard error msg from setup'),
                ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__TWICE +
                PRE_SDS_VALIDATION_STEPS__TWICE +
                [phase_step.SETUP__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 ],
            ))

    def test_hard_error_exception(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.SETUP,
                 test.setup_phase_instruction_that(
                     main=do_raise(hard_error_ex('hard error exception msg from setup'))))
        self._check(
            Arrangement(test_case),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.HARD_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.SETUP__MAIN,
                        test_case.the_extra(PartialPhase.SETUP)[0].source,
                        'hard error exception msg from setup'),
                ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__TWICE +
                PRE_SDS_VALIDATION_STEPS__TWICE +
                [phase_step.SETUP__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 ],
            ))

    def test_internal_error(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.SETUP,
                 test.setup_phase_instruction_that(
                     main=do_raise(test.ImplementationErrorTestException())))
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_returns_exit_code(5)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.INTERNAL_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_exception(
                        phase_step.SETUP__MAIN,
                        test_case.the_extra(PartialPhase.SETUP)[0].source,
                        test.ImplementationErrorTestException),
                ),
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__TWICE +
                PRE_SDS_VALIDATION_STEPS__TWICE +
                [phase_step.SETUP__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 ],
            ))


class TestBeforeAssertMainStep(TestCaseBase):
    def test_hard_error(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.BEFORE_ASSERT,
                 test.before_assert_phase_instruction_that(
                     main=do_return(sh.new_sh_hard_error__str('hard error msg'))))
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_returns_exit_code(0)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.HARD_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(0),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.BEFORE_ASSERT__MAIN,
                        test_case.the_extra(PartialPhase.BEFORE_ASSERT)[0].source,
                        'hard error msg'),
                ),
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__TWICE +
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

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 phase_step.BEFORE_ASSERT__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.BEFORE_ASSERT),
                 (phase_step.CLEANUP__MAIN, PreviousPhase.BEFORE_ASSERT),
                 ],
            ))

    def test_hard_error_exception(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.BEFORE_ASSERT,
                 test.before_assert_phase_instruction_that(
                     main=do_raise(hard_error_ex('hard error exception msg'))))
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_returns_exit_code(0)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.HARD_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(0),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.BEFORE_ASSERT__MAIN,
                        test_case.the_extra(PartialPhase.BEFORE_ASSERT)[0].source,
                        'hard error exception msg'),
                ),
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__TWICE +
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

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 phase_step.BEFORE_ASSERT__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.BEFORE_ASSERT),
                 (phase_step.CLEANUP__MAIN, PreviousPhase.BEFORE_ASSERT),
                 ],
            ))

    def test_internal_error(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.BEFORE_ASSERT,
                 test.before_assert_phase_instruction_that(
                     main=do_raise(test.ImplementationErrorTestException())))
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_returns_exit_code(12)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.INTERNAL_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(12),
                    ExpectedFailureForInstructionFailure.new_with_exception(
                        phase_step.BEFORE_ASSERT__MAIN,
                        test_case.the_extra(PartialPhase.BEFORE_ASSERT)[0].source,
                        test.ImplementationErrorTestException),
                ),
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__TWICE +
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

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 phase_step.BEFORE_ASSERT__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.BEFORE_ASSERT),
                 (phase_step.CLEANUP__MAIN, PreviousPhase.BEFORE_ASSERT),
                 ],
            ))


class TestAssertMainStep(TestCaseBase):
    def test_fail(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that(
                     main=do_return(pfh.new_pfh_fail__str('fail msg from ASSERT'))))
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_returns_exit_code(5)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.FAIL,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(5),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.ASSERT__MAIN,
                        test_case.the_extra(PartialPhase.ASSERT)[0].source,
                        'fail msg from ASSERT'),
                ),
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__TWICE +
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

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.ASSERT__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 ],
            ))

    def test_hard_error(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that(
                     main=do_return(pfh.new_pfh_hard_error__str('hard error msg from ASSERT'))))
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_returns_exit_code(72)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.HARD_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(72),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.ASSERT__MAIN,
                        test_case.the_extra(PartialPhase.ASSERT)[0].source,
                        'hard error msg from ASSERT'),
                ),
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__TWICE +
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

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.ASSERT__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 ],
            ))

    def test_hard_error_exception(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that(
                     main=do_raise(hard_error_ex('hard error exception msg from ASSERT'))))
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_returns_exit_code(72)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.HARD_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(72),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.ASSERT__MAIN,
                        test_case.the_extra(PartialPhase.ASSERT)[0].source,
                        'hard error exception msg from ASSERT'),
                ),
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__TWICE +
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

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.ASSERT__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 ],
            ))

    def test_internal_error(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that(
                     main=do_raise(test.ImplementationErrorTestException())))
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_returns_exit_code(5)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.INTERNAL_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(5),
                    ExpectedFailureForInstructionFailure.new_with_exception(
                        phase_step.ASSERT__MAIN,
                        test_case.the_extra(PartialPhase.ASSERT)[0].source,
                        test.ImplementationErrorTestException),
                ),
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__TWICE +
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

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.ASSERT__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 ],
            ))


class TestCleanupMainStep(TestCaseBase):
    def test_hard_error(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.CLEANUP,
                 test.cleanup_phase_instruction_that(
                     main=do_return(sh.new_sh_hard_error__str('hard error msg from CLEANUP'))))
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_returns_exit_code(3)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.HARD_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(3),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.CLEANUP__MAIN,
                        test_case.the_extra(PartialPhase.CLEANUP)[0].source,
                        'hard error msg from CLEANUP'),
                ),
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__TWICE +
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

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.ASSERT__MAIN,
                 phase_step.ASSERT__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 ],
            ))

    def test_hard_error_exception(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.CLEANUP,
                 test.cleanup_phase_instruction_that(
                     main=do_raise(hard_error_ex('hard error exception msg from CLEANUP'))))
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_returns_exit_code(3)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.HARD_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(3),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.CLEANUP__MAIN,
                        test_case.the_extra(PartialPhase.CLEANUP)[0].source,
                        'hard error exception msg from CLEANUP'),
                ),
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__TWICE +
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

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.ASSERT__MAIN,
                 phase_step.ASSERT__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 ],
            ))

    def test_internal_error(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(PartialPhase.CLEANUP,
                 test.cleanup_phase_instruction_that(
                     main=do_raise(test.ImplementationErrorTestException())))
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_returns_exit_code(5)),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.INTERNAL_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(5),
                    ExpectedFailureForInstructionFailure.new_with_exception(
                        phase_step.CLEANUP__MAIN,
                        test_case.the_extra(PartialPhase.CLEANUP)[0].source,
                        test.ImplementationErrorTestException),
                ),
                [phase_step.ACT__PARSE] +

                SYMBOL_VALIDATION_STEPS__TWICE +
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

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.BEFORE_ASSERT__MAIN,
                 phase_step.ASSERT__MAIN,
                 phase_step.ASSERT__MAIN,
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 ],
            ))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
