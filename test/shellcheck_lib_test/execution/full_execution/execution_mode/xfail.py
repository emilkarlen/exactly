import unittest

from shellcheck_lib.execution import phase_step, phases
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.sections.anonymous import ExecutionMode
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib_test.execution.full_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase, one_successful_instruction_in_each_phase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_EDS_VALIDATION_STEPS
from shellcheck_lib_test.execution.test_resources.instruction_test_resources import do_return
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForInstructionFailure, \
    ExpectedFailureForNoFailure


class Test(TestCaseBase):
    def test_with_assert_phase_that_fails(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL)) \
            .add(phases.ASSERT,
                 test.assert_phase_instruction_that(
                         main=test.do_return(pfh.new_pfh_fail('fail message'))))
        self._check(Arrangement(test_case),
                    Expectation(FullResultStatus.XFAIL,
                                ExpectedFailureForInstructionFailure.new_with_message(
                                        phase_step.ASSERT_MAIN,
                                        test_case.the_extra(phases.ASSERT)[0].first_line,
                                        'fail message'),
                                [phase_step.ANONYMOUS_MAIN] +
                                PRE_EDS_VALIDATION_STEPS +
                                [phase_step.SETUP_MAIN,
                                 phase_step.SETUP_POST_VALIDATE,
                                 phase_step.ACT_VALIDATE_POST_EDS,
                                 phase_step.ASSERT_VALIDATE_POST_EDS,
                                 phase_step.ACT_MAIN,
                                 phase_step.ACT_SCRIPT_VALIDATE,
                                 phase_step.ACT_SCRIPT_EXECUTE,
                                 phase_step.ASSERT_MAIN,
                                 phase_step.CLEANUP_MAIN,
                                 ],
                                True))

    def test_with_assert_phase_that_passes(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.XPASS,
                            ExpectedFailureForNoFailure(),
                            [phase_step.ANONYMOUS_MAIN] +
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.ASSERT_VALIDATE_POST_EDS,
                             phase_step.ACT_MAIN,
                             phase_step.ACT_SCRIPT_VALIDATE,
                             phase_step.ACT_SCRIPT_EXECUTE,
                             phase_step.ASSERT_MAIN,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_with_anonymous_phase_with_hard_error(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL)) \
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

    def test_with_implementation_error(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL)) \
            .add(phases.CLEANUP,
                 test.cleanup_phase_instruction_that(
                         main=test.do_raise(test.ImplementationErrorTestException())))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.CLEANUP_MAIN,
                                    test_case.the_extra(phases.CLEANUP)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.ANONYMOUS_MAIN] +
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.ASSERT_VALIDATE_POST_EDS,
                             phase_step.ACT_MAIN,
                             phase_step.ACT_SCRIPT_VALIDATE,
                             phase_step.ACT_SCRIPT_EXECUTE,
                             phase_step.ASSERT_MAIN,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
