import unittest

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.result import pfh, sh
from exactly_lib.test_case.test_case_status import TestCaseStatus
from exactly_lib_test.execution.full_execution.test_resources import result_assertions as asrt_result
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    test_case_with_two_instructions_in_each_phase
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_SDS_VALIDATION_STEPS__TWICE, \
    SYMBOL_VALIDATION_STEPS__TWICE
from exactly_lib_test.execution.test_resources.failure_info_check import ExpectedFailureForInstructionFailure
from exactly_lib_test.execution.test_resources.result_assertions import action_to_check_has_executed_completely
from exactly_lib_test.test_case.actor.test_resources.test_actions import \
    execute_action_that_returns_exit_code
from exactly_lib_test.test_resources.actions import do_return, do_raise


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(TestCaseBase):
    def test_with_assert_phase_that_fails(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(TestCaseStatus.FAIL)) \
            .add(phase_identifier.ASSERT,
                 test.assert_phase_instruction_that(
                     main=do_return(pfh.new_pfh_fail__str('fail message'))))
        self._check(Arrangement(test_case,
                                execute_test_action=execute_action_that_returns_exit_code(11)),
                    Expectation(
                        asrt_result.matches2(
                            FullExeResultStatus.XFAIL,
                            asrt_result.has_sds(),
                            asrt_result.has_action_to_check_outcome_with_exit_code(11),
                            ExpectedFailureForInstructionFailure.new_with_message(
                                phase_step.ASSERT__MAIN,
                                test_case.the_extra(phase_identifier.ASSERT)[0].source,
                                'fail message'),
                        ),
                        [phase_step.CONFIGURATION__MAIN,
                         phase_step.CONFIGURATION__MAIN] +
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

                         phase_step.ACT__PREPARE,
                         phase_step.ACT__EXECUTE,

                         phase_step.BEFORE_ASSERT__MAIN,
                         phase_step.BEFORE_ASSERT__MAIN,
                         phase_step.ASSERT__MAIN,
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         ],
                    ))

    def test_with_assert_phase_that_passes(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(TestCaseStatus.FAIL))
        self._check(
            Arrangement(test_case,
                        execute_test_action=execute_action_that_returns_exit_code(64)),
            Expectation(asrt_result.is_xpass(action_to_check_outcome=action_to_check_has_executed_completely(64)),
                        [phase_step.CONFIGURATION__MAIN,
                         phase_step.CONFIGURATION__MAIN] +
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

                         phase_step.ACT__PREPARE,
                         phase_step.ACT__EXECUTE,

                         phase_step.BEFORE_ASSERT__MAIN,
                         phase_step.BEFORE_ASSERT__MAIN,
                         phase_step.ASSERT__MAIN,
                         phase_step.ASSERT__MAIN,
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                         ],
                        ))

    def test_with_configuration_phase_with_hard_error(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(TestCaseStatus.FAIL)) \
            .add(phase_identifier.CONFIGURATION,
                 test.configuration_phase_instruction_that(do_return(sh.new_sh_hard_error__str('hard error msg'))))
        self._check(
            Arrangement(test_case),
            Expectation(
                asrt_result.matches2(
                    FullExeResultStatus.HARD_ERROR,
                    asrt_result.has_no_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.CONFIGURATION__MAIN,
                        test_case.the_extra(phase_identifier.CONFIGURATION)[1].source,
                        'hard error msg'),
                ),
                [phase_step.CONFIGURATION__MAIN],
            ))

    def test_with_implementation_error(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(TestCaseStatus.FAIL)) \
            .add(phase_identifier.CLEANUP,
                 test.cleanup_phase_instruction_that(
                     main=do_raise(test.ImplementationErrorTestException())))
        self._check(
            Arrangement(test_case,
                        execute_test_action=execute_action_that_returns_exit_code(128)),
            Expectation(
                asrt_result.matches2(
                    FullExeResultStatus.IMPLEMENTATION_ERROR,
                    asrt_result.has_sds(),
                    asrt_result.has_action_to_check_outcome_with_exit_code(128),
                    ExpectedFailureForInstructionFailure.new_with_exception(
                        phase_step.CLEANUP__MAIN,
                        test_case.the_extra(phase_identifier.CLEANUP)[0].source,
                        test.ImplementationErrorTestException),
                ),
                [phase_step.CONFIGURATION__MAIN,
                 phase_step.CONFIGURATION__MAIN] +
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
