import unittest

from shellcheck_lib.execution import phase_step, phases
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.sections.anonymous import ExecutionMode
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib_test.execution.full_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase, one_successful_instruction_in_each_phase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.execution.test_resources.instruction_test_resources import do_return
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForNoFailure, \
    ExpectedFailureForInstructionFailure


class Test(TestCaseBase):
    def test_execution_mode_skipped(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(
                         ExecutionMode.SKIPPED))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.SKIPPED,
                            ExpectedFailureForNoFailure(),
                            [phase_step.ANONYMOUS_MAIN],
                            False))

    def test_execution_mode_skipped_but_failing_instruction_in_anonymous_phase_before_setting_execution_mode(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(phases.ANONYMOUS,
                 test.anonymous_phase_instruction_that(do_return(sh.new_sh_hard_error('hard error msg')))) \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(
                         ExecutionMode.SKIPPED))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ANONYMOUS_MAIN,
                                    test_case.the_extra(phases.ANONYMOUS)[0].first_line,
                                    'hard error msg'),
                            [phase_step.ANONYMOUS_MAIN],
                            False))

    def test_execution_mode_skipped_but_failing_instruction_in_anonymous_phase_after_setting_execution_mode(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(
                         ExecutionMode.SKIPPED)) \
            .add(phases.ANONYMOUS,
                 test.anonymous_phase_instruction_that(do_return(sh.new_sh_hard_error('hard error msg'))))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ANONYMOUS_MAIN,
                                    test_case.the_extra(phases.ANONYMOUS)[1].first_line,
                                    'hard error msg'),
                            [phase_step.ANONYMOUS_MAIN],
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
