import unittest

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution.full_execution.result import FullExeResultStatus
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.result import sh
from exactly_lib.test_case.test_case_status import TestCaseStatus
from exactly_lib_test.execution.full_execution.test_resources import result_assertions as asrt_result
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    test_case_with_two_instructions_in_each_phase
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.failure_info_check import ExpectedFailureForInstructionFailure
from exactly_lib_test.test_resources.actions import do_return


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(TestCaseBase):
    def test_execution_mode_skipped(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(
                     TestCaseStatus.SKIP))
        self._check(
            Arrangement(test_case),
            Expectation(asrt_result.is_skipped(),
                        [phase_step.CONFIGURATION__MAIN,
                         phase_step.CONFIGURATION__MAIN],
                        ))

    def test_execution_mode_skipped_but_failing_instruction_in_configuration_phase_before_setting_execution_mode(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.configuration_phase_instruction_that(do_return(sh.new_sh_hard_error__const('hard error msg')))) \
            .add(phase_identifier.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(
                     TestCaseStatus.SKIP))
        self._check(
            Arrangement(test_case),
            Expectation(
                asrt_result.matches2(
                    FullExeResultStatus.HARD_ERROR,
                    asrt_result.has_no_sds(),
                    asrt_result.has_no_action_to_check_outcome(),
                    ExpectedFailureForInstructionFailure.new_with_message(
                        phase_step.CONFIGURATION__MAIN,
                        test_case.the_extra(phase_identifier.CONFIGURATION)[0].source,
                        'hard error msg')
                ),
                [phase_step.CONFIGURATION__MAIN],
            ))

    def test_execution_mode_skipped_but_failing_instruction_in_configuration_phase_after_setting_execution_mode(self):
        test_case = test_case_with_two_instructions_in_each_phase() \
            .add(phase_identifier.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(
                     TestCaseStatus.SKIP)) \
            .add(phase_identifier.CONFIGURATION,
                 test.configuration_phase_instruction_that(do_return(sh.new_sh_hard_error__const('hard error msg'))))
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
                        'hard error msg')),
                [phase_step.CONFIGURATION__MAIN],
            ))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
