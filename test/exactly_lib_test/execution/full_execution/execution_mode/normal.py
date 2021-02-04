import unittest

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.result import svh
from exactly_lib_test.execution.full_execution.test_resources import result_assertions as asrt_result
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    test_case_with_two_instructions_in_each_phase
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.partial_execution.test_resources.hard_error_ex import hard_error_ex
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
    def test_full_sequence(self):
        self._check(
            Arrangement(test_case_with_two_instructions_in_each_phase(),
                        execute_test_action=execute_action_that_returns_exit_code(72)),
            Expectation(
                asrt_result.is_pass(action_to_check_outcome=action_to_check_has_executed_completely(72)
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
                 (phase_step.CLEANUP__MAIN, PreviousPhase.ASSERT),
                 ],
            ))

    def test_validation_error_in_configuration_phase(self):
        err_msg = 'the error msg'
        test_case_generator = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.configuration_phase_instruction_that(do_return(svh.new_svh_validation_error__str(err_msg))))
        self._check(
            Arrangement(test_case_generator),
            Expectation(
                asrt_result.matches2(
                    FullExeResultStatus.VALIDATION_ERROR,
                    asrt_result.has_no_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.CONFIGURATION__MAIN,
                        test_case_generator.the_extra(phase_identifier.CONFIGURATION)[0].source,
                        err_msg)
                ),
                [phase_step.CONFIGURATION__MAIN],
            )
        )

    def test_hard_error_in_configuration_phase(self):
        test_case_generator = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.configuration_phase_instruction_that(do_return(svh.new_svh_hard_error__str('hard error msg'))))
        self._check(
            Arrangement(test_case_generator),
            Expectation(
                asrt_result.matches2(
                    FullExeResultStatus.HARD_ERROR,
                    asrt_result.has_no_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.CONFIGURATION__MAIN,
                        test_case_generator.the_extra(phase_identifier.CONFIGURATION)[
                            0].source,
                        'hard error msg')
                ),
                [phase_step.CONFIGURATION__MAIN],
            ))

    def test_hard_error_exception_in_configuration_phase(self):
        err_msg = 'the error message'
        test_case_generator = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.configuration_phase_instruction_that(do_raise(
                     hard_error_ex(err_msg))
                 ))
        self._check(
            Arrangement(test_case_generator),
            Expectation(
                asrt_result.matches2(
                    FullExeResultStatus.HARD_ERROR,
                    asrt_result.has_no_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.CONFIGURATION__MAIN,
                        test_case_generator.the_extra(phase_identifier.CONFIGURATION)[
                            0].source,
                        err_msg)
                ),
                [phase_step.CONFIGURATION__MAIN],
            )
        )

    def test_internal_error_in_configuration_phase(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.configuration_phase_instruction_that(
                     main=do_raise(test.ImplementationErrorTestException())))
        self._check(
            Arrangement(test_case),
            Expectation(
                asrt_result.matches2(
                    FullExeResultStatus.INTERNAL_ERROR,
                    asrt_result.has_no_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_exception(
                        phase_step.CONFIGURATION__MAIN,
                        test_case.the_extra(phase_identifier.CONFIGURATION)[0].source,
                        test.ImplementationErrorTestException),
                ),
                [phase_step.CONFIGURATION__MAIN],
            ))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
