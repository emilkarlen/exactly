import unittest
from typing import Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.result import ExecutionFailureStatus
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.result import svh
from exactly_lib_test.execution.partial_execution.test_resources import result_assertions as asrt_result
from exactly_lib_test.execution.partial_execution.test_resources.hard_error_ex import hard_error_ex
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList, \
    TestCaseGeneratorForExecutionRecording
from exactly_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import \
    PRE_SDS_VALIDATION_STEPS__ONCE, SYMBOL_VALIDATION_STEPS__ONCE
from exactly_lib_test.execution.test_resources.failure_info_check import ExpectedFailureForPhaseFailure
from exactly_lib_test.test_case.actor.test_resources.test_actions import execute_action_that_raises, \
    execute_action_that_returns_hard_error_with_message, \
    prepare_action_that_returns_hard_error_with_message, validate_action_that_returns, validate_action_that_raises, \
    prepare_action_that_raises


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValidatePreSds),
        unittest.makeSuite(TestValidatePostSetup),
        unittest.makeSuite(TestValidationOfExecutionInput),
        unittest.makeSuite(TestPrepare),
        unittest.makeSuite(TestExecute),
    ])


class TestValidatePreSds(TestCaseBase):
    def test_hard_error(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        atc_validate_pre_sds=validate_action_that_returns(
                            svh.new_svh_hard_error__str('error in act/validate-pre-sds'))),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.HARD_ERROR,
                                     asrt_result.has_no_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_message(
                                         phase_step.ACT__VALIDATE_PRE_SDS,
                                         'error in act/validate-pre-sds')
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                [
                    phase_step.SETUP__VALIDATE_PRE_SDS,
                    phase_step.ACT__VALIDATE_PRE_SDS,
                ],
            ))

    def test_hard_error_exception(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(
                test_case,
                atc_validate_pre_sds=validate_action_that_raises(
                    hard_error_ex('HE exception in act/validate-pre-sds'))
            ),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.HARD_ERROR,
                                     asrt_result.has_no_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_message(
                                         phase_step.ACT__VALIDATE_PRE_SDS,
                                         'HE exception in act/validate-pre-sds')
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                [
                    phase_step.SETUP__VALIDATE_PRE_SDS,
                    phase_step.ACT__VALIDATE_PRE_SDS,
                ],
            ))

    def test_validation_error(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        atc_validate_pre_sds=validate_action_that_returns(
                            svh.new_svh_validation_error__str('error in act/validate-pre-sds'))),
            Expectation(
                asrt_result.matches2(
                    ExecutionFailureStatus.VALIDATION_ERROR,
                    asrt_result.has_no_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForPhaseFailure.new_with_message(
                        phase_step.ACT__VALIDATE_PRE_SDS,
                        'error in act/validate-pre-sds'),
                ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                [
                    phase_step.SETUP__VALIDATE_PRE_SDS,
                    phase_step.ACT__VALIDATE_PRE_SDS,
                ],
            ))

    def test_exception(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        atc_validate_pre_sds=validate_action_that_raises(
                            test.ImplementationErrorTestException())),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.INTERNAL_ERROR,
                                     asrt_result.has_no_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_exception(
                                         phase_step.ACT__VALIDATE_PRE_SDS,
                                         test.ImplementationErrorTestException)),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                [
                    phase_step.SETUP__VALIDATE_PRE_SDS,
                    phase_step.ACT__VALIDATE_PRE_SDS,
                ],
            ))


class TestValidatePostSetup(TestCaseBase):
    def test_validation_error(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        atc_validate_post_setup=validate_action_that_returns(
                            svh.new_svh_validation_error__str('error in act/validate-post-setup'))),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.VALIDATION_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_message(
                                         phase_step.ACT__VALIDATE_POST_SETUP,
                                         'error in act/validate-post-setup'),
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [
                    phase_step.SETUP__MAIN,

                    phase_step.SETUP__VALIDATE_POST_SETUP,
                    phase_step.ACT__VALIDATE_POST_SETUP,

                    (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                ],
            ))

    def test_hard_error(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        atc_validate_post_setup=validate_action_that_returns(
                            svh.new_svh_hard_error__str('error in act/validate-post-setup'))),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.HARD_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_message(
                                         phase_step.ACT__VALIDATE_POST_SETUP,
                                         'error in act/validate-post-setup')
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [
                    phase_step.SETUP__MAIN,

                    phase_step.SETUP__VALIDATE_POST_SETUP,
                    phase_step.ACT__VALIDATE_POST_SETUP,

                    (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                ],
            ))

    def test_hard_exception(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(
                test_case,
                atc_validate_post_setup=validate_action_that_raises(
                    hard_error_ex('HE exception in act/validate-post-setup'))
            ),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.HARD_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_message(
                                         phase_step.ACT__VALIDATE_POST_SETUP,
                                         'HE exception in act/validate-post-setup')
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [
                    phase_step.SETUP__MAIN,

                    phase_step.SETUP__VALIDATE_POST_SETUP,
                    phase_step.ACT__VALIDATE_POST_SETUP,

                    (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                ],
            ))

    def test_exception(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        atc_validate_post_setup=validate_action_that_raises(
                            test.ImplementationErrorTestException())),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.INTERNAL_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_exception(
                                         phase_step.ACT__VALIDATE_POST_SETUP,
                                         test.ImplementationErrorTestException)
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [
                    phase_step.SETUP__MAIN,

                    phase_step.SETUP__VALIDATE_POST_SETUP,
                    phase_step.ACT__VALIDATE_POST_SETUP,

                    (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                ],
            ))


class TestValidationOfExecutionInput(TestCaseBase):
    def test_hard_error(self):
        failure_message = 'error in act/prepare'

        def validator_that_reports_error() -> Optional[TextRenderer]:
            return text_docs.single_pre_formatted_line_object(failure_message)

        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case),
            custom_act_execution_input_validator=validator_that_reports_error,
            expectation=Expectation(
                asrt_result.matches2(ExecutionFailureStatus.HARD_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_message(
                                         phase_step.ACT__VALIDATE_EXE_INPUT,
                                         failure_message)
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 ],
            ))

    def test_hard_error_exception(self):
        failure_message = 'HE exception in act/validate exe info'

        def validator_that_raises_hard_error() -> Optional[TextRenderer]:
            raise hard_error_ex(failure_message)

        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case),
            custom_act_execution_input_validator=validator_that_raises_hard_error,
            expectation=Expectation(
                asrt_result.matches2(ExecutionFailureStatus.HARD_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_message(
                                         phase_step.ACT__VALIDATE_EXE_INPUT,
                                         failure_message)
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 ],
            ))

    def test_internal_error(self):
        def validator_that_raises_exception() -> Optional[TextRenderer]:
            raise test.ImplementationErrorTestException()

        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case, ),
            custom_act_execution_input_validator=validator_that_raises_exception,
            expectation=Expectation(
                asrt_result.matches2(ExecutionFailureStatus.INTERNAL_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_exception(
                                         phase_step.ACT__VALIDATE_EXE_INPUT,
                                         test.ImplementationErrorTestException),
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 ],
            ))


class TestPrepare(TestCaseBase):
    def test_hard_error(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        atc_prepare=prepare_action_that_returns_hard_error_with_message(
                            'error in act/prepare')),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.HARD_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_message(
                                         phase_step.ACT__PREPARE,
                                         'error in act/prepare')
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,

                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 ],
            ))

    def test_hard_error_exception(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(
                test_case,
                atc_prepare=prepare_action_that_raises(
                    hard_error_ex('HE exception in act/prepare'))
            ),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.HARD_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_message(
                                         phase_step.ACT__PREPARE,
                                         'HE exception in act/prepare')
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,

                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 ],
            ))

    def test_internal_error(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        atc_prepare=prepare_action_that_raises(
                            test.ImplementationErrorTestException())),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.INTERNAL_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_exception(
                                         phase_step.ACT__PREPARE,
                                         test.ImplementationErrorTestException),
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,

                 (phase_step.CLEANUP__MAIN, PreviousPhase.SETUP),
                 ],
            ))


class TestExecute(TestCaseBase):
    def test_hard_error(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_returns_hard_error_with_message(
                            'error in execute')),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.HARD_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_message(
                                         phase_step.ACT__EXECUTE,
                                         'error in execute')
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 (phase_step.CLEANUP__MAIN, PreviousPhase.ACT),
                 ],
            ))

    def test_hard_error_exception(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_raises(
                            hard_error_ex('HE exception in execute'))),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.HARD_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_message(
                                         phase_step.ACT__EXECUTE,
                                         'HE exception in execute')
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 (phase_step.CLEANUP__MAIN, PreviousPhase.ACT),
                 ],
            ))

    def test_internal_error(self):
        test_case = _single_successful_instruction_in_each_phase()
        self._check(
            Arrangement(test_case,
                        atc_execute=execute_action_that_raises(
                            test.ImplementationErrorTestException())),
            Expectation(
                asrt_result.matches2(ExecutionFailureStatus.INTERNAL_ERROR,
                                     asrt_result.has_sds(),
                                     asrt_result.has_no_action_to_check_outcome(),
                                     ExpectedFailureForPhaseFailure.new_with_exception(
                                         phase_step.ACT__EXECUTE,
                                         test.ImplementationErrorTestException)
                                     ),
                [phase_step.ACT__PARSE] +
                SYMBOL_VALIDATION_STEPS__ONCE +
                PRE_SDS_VALIDATION_STEPS__ONCE +
                [phase_step.SETUP__MAIN,

                 phase_step.SETUP__VALIDATE_POST_SETUP,
                 phase_step.ACT__VALIDATE_POST_SETUP,
                 phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
                 phase_step.ASSERT__VALIDATE_POST_SETUP,

                 phase_step.ACT__VALIDATE_EXE_INPUT,

                 phase_step.ACT__PREPARE,
                 phase_step.ACT__EXECUTE,

                 (phase_step.CLEANUP__MAIN, PreviousPhase.ACT),
                 ],
            ))


def _single_successful_instruction_in_each_phase() -> TestCaseGeneratorForExecutionRecording:
    return TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
