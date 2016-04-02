import unittest

from shellcheck_lib.execution import phase_step_simple as phase_step
from shellcheck_lib.execution import phases
from shellcheck_lib.execution.execution_mode import ExecutionMode
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib_test.execution.full_execution.test_resources.recording.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr
from shellcheck_lib_test.execution.full_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.execution.test_resources.instruction_test_resources import do_return
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForNoFailure, \
    ExpectedFailureForInstructionFailure


class Test(TestCaseBase):
    def test_execution_mode_skipped(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(
                         ExecutionMode.SKIP))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.SKIPPED,
                            ExpectedFailureForNoFailure(),
                            [phase_step.ANONYMOUS__MAIN,
                             phase_step.ANONYMOUS__MAIN],
                            False))

    def test_execution_mode_skipped_but_failing_instruction_in_anonymous_phase_before_setting_execution_mode(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(phases.ANONYMOUS,
                 test.anonymous_phase_instruction_that(do_return(sh.new_sh_hard_error('hard error msg')))) \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(
                         ExecutionMode.SKIP))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ANONYMOUS__MAIN,
                                    test_case.the_extra(phases.ANONYMOUS)[0].first_line,
                                    'hard error msg'),
                            [phase_step.ANONYMOUS__MAIN],
                            False))

    def test_execution_mode_skipped_but_failing_instruction_in_anonymous_phase_after_setting_execution_mode(self):
        test_case = TestCaseGeneratorWithExtraInstrsBetweenRecordingInstr() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(
                         ExecutionMode.SKIP)) \
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

        if __name__ == '__main__':
            unittest.main()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
