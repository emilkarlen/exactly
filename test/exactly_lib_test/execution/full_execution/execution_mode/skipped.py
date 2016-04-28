import unittest

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.execution import phases
from exactly_lib.execution.execution_mode import ExecutionMode
from exactly_lib.execution.result import FullResultStatus
from exactly_lib.test_case.phases.result import sh
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr
from exactly_lib_test.execution.full_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from exactly_lib_test.execution.test_resources import instruction_test_resources as test
from exactly_lib_test.execution.test_resources.instruction_test_resources import do_return
from exactly_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForNoFailure, \
    ExpectedFailureForInstructionFailure


class Test(TestCaseBase):
    def test_execution_mode_skipped(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(phases.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(
                         ExecutionMode.SKIP))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.SKIPPED,
                            ExpectedFailureForNoFailure(),
                            [phase_step.CONFIGURATION__MAIN,
                             phase_step.CONFIGURATION__MAIN],
                            False))

    def test_execution_mode_skipped_but_failing_instruction_in_configuration_phase_before_setting_execution_mode(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(phases.CONFIGURATION,
                 test.configuration_phase_instruction_that(do_return(sh.new_sh_hard_error('hard error msg')))) \
            .add(phases.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(
                         ExecutionMode.SKIP))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.CONFIGURATION__MAIN,
                                    test_case.the_extra(phases.CONFIGURATION)[0].first_line,
                                    'hard error msg'),
                            [phase_step.CONFIGURATION__MAIN],
                            False))

    def test_execution_mode_skipped_but_failing_instruction_in_configuration_phase_after_setting_execution_mode(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(phases.CONFIGURATION,
                 test.ConfigurationPhaseInstructionThatSetsExecutionMode(
                         ExecutionMode.SKIP)) \
            .add(phases.CONFIGURATION,
                 test.configuration_phase_instruction_that(do_return(sh.new_sh_hard_error('hard error msg'))))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.CONFIGURATION__MAIN,
                                    test_case.the_extra(phases.CONFIGURATION)[1].first_line,
                                    'hard error msg'),
                            [phase_step.CONFIGURATION__MAIN],
                            False))

        if __name__ == '__main__':
            unittest.main()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
