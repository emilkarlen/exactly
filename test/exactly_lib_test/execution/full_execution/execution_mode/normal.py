import unittest

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.full_execution.result import FullResultStatus
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.result import sh
from exactly_lib_test.execution.full_execution.test_resources import result_assertions as asrt_full_result
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    test_case_with_two_instructions_in_each_phase
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_SDS_VALIDATION_STEPS__TWICE, \
    SYMBOL_VALIDATION_STEPS__TWICE
from exactly_lib_test.execution.test_resources.failure_info_check import ExpectedFailureForInstructionFailure
from exactly_lib_test.test_resources.actions import do_return, do_raise


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(TestCaseBase):
    def test_full_sequence(self):
        self._check(
            Arrangement(test_case_with_two_instructions_in_each_phase()),
            Expectation(asrt_full_result.is_pass(),
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
                        True))

    def test_hard_error_in_configuration_phase(self):
        test_case_generator = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.configuration_phase_instruction_that(do_return(sh.new_sh_hard_error('hard error msg'))))
        self._check(
            Arrangement(test_case_generator),
            Expectation(asrt_full_result.is_failure(FullResultStatus.HARD_ERROR,
                                                    ExpectedFailureForInstructionFailure.new_with_message(
                                                        phase_step.CONFIGURATION__MAIN,
                                                        test_case_generator.the_extra(phase_identifier.CONFIGURATION)[
                                                            0].source,
                                                        'hard error msg')),
                        [phase_step.CONFIGURATION__MAIN],
                        False))

    def test_implementation_error_in_configuration_phase(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.configuration_phase_instruction_that(
                     main=do_raise(test.ImplementationErrorTestException())))
        self._check(
            Arrangement(test_case),
            Expectation(asrt_full_result.is_failure(FullResultStatus.IMPLEMENTATION_ERROR,
                                                    ExpectedFailureForInstructionFailure.new_with_exception(
                                                        phase_step.CONFIGURATION__MAIN,
                                                        test_case.the_extra(phase_identifier.CONFIGURATION)[0].source,
                                                        test.ImplementationErrorTestException)),
                        [phase_step.CONFIGURATION__MAIN],
                        False))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
