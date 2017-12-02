import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step_simple as phase_step
from exactly_lib.execution.result import FullResultStatus
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.test_case_status import ExecutionMode
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    test_case_with_two_instructions_in_each_phase
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_SDS_VALIDATION_STEPS__TWICE, \
    SYMBOL_VALIDATION_STEPS__TWICE
from exactly_lib_test.test_resources.actions import do_return, do_raise
from exactly_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForInstructionFailure, \
    ExpectedFailureForNoFailure


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(TestCaseBase):
    def test_with_assert_phase_that_fails(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(ExecutionMode.FAIL)) \
            .add(phase_identifier.ASSERT,
                 test.assert_phase_instruction_that(
                     main=do_return(pfh.new_pfh_fail('fail message'))))
        self._check(Arrangement(test_case),
                    Expectation(FullResultStatus.XFAIL,
                                ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ASSERT__MAIN,
                                    test_case.the_extra(phase_identifier.ASSERT)[0].first_line,
                                    'fail message'),
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
                                True))

    def test_with_assert_phase_that_passes(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(ExecutionMode.FAIL))
        self._check(
            Arrangement(test_case),
            Expectation(FullResultStatus.XPASS,
                        ExpectedFailureForNoFailure(),
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

    def test_with_configuration_phase_with_hard_error(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(ExecutionMode.FAIL)) \
            .add(phase_identifier.CONFIGURATION,
                 test.configuration_phase_instruction_that(do_return(sh.new_sh_hard_error('hard error msg'))))
        self._check(
            Arrangement(test_case),
            Expectation(FullResultStatus.HARD_ERROR,
                        ExpectedFailureForInstructionFailure.new_with_message(
                            phase_step.CONFIGURATION__MAIN,
                            test_case.the_extra(phase_identifier.CONFIGURATION)[1].first_line,
                            'hard error msg'),
                        [phase_step.CONFIGURATION__MAIN],
                        False))

    def test_with_implementation_error(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(ExecutionMode.FAIL)) \
            .add(phase_identifier.CLEANUP,
                 test.cleanup_phase_instruction_that(
                     main=do_raise(test.ImplementationErrorTestException())))
        self._check(
            Arrangement(test_case),
            Expectation(FullResultStatus.IMPLEMENTATION_ERROR,
                        ExpectedFailureForInstructionFailure.new_with_exception(
                            phase_step.CLEANUP__MAIN,
                            test_case.the_extra(phase_identifier.CLEANUP)[0].first_line,
                            test.ImplementationErrorTestException),
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
                        True))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
