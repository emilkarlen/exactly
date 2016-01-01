import unittest

from shellcheck_lib.execution import phase_step, phases
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.sections.anonymous import ExecutionMode
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.full_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase, one_successful_instruction_in_each_phase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForInstructionFailure, \
    ExpectedFailureForNoFailure


class Test(TestCaseBase):
    def test_with_assert_phase_that_fails(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL)) \
            .add(phases.ASSERT,
                 test.AssertPhaseInstructionThatReturns(
                         from_validate=svh.new_svh_success(),
                         from_execute=pfh.new_pfh_fail('fail message')))
        self._check(Arrangement(test_case),
                    Expectation(FullResultStatus.XFAIL,
                                ExpectedFailureForInstructionFailure.new_with_message(
                                        phase_step.PhaseStep(phases.ASSERT, phase_step.EXECUTE),
                                        test_case.the_extra(phases.ASSERT)[0].first_line,
                                        'fail message'),
                                [phase_step.ANONYMOUS,
                                 phase_step.SETUP__PRE_VALIDATE,
                                 phase_step.SETUP__EXECUTE,
                                 phase_step.SETUP__POST_VALIDATE,
                                 phase_step.ACT__VALIDATE,
                                 phase_step.ASSERT__VALIDATE,
                                 phase_step.ACT__SCRIPT_GENERATE,
                                 phase_step.ACT__SCRIPT_VALIDATE,
                                 phase_step.ACT__SCRIPT_EXECUTE,
                                 phase_step.ASSERT__EXECUTE,
                                 phase_step.CLEANUP
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
                            [phase_step.ANONYMOUS,
                             phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.ACT__SCRIPT_GENERATE,
                             phase_step.ACT__SCRIPT_VALIDATE,
                             phase_step.ACT__SCRIPT_EXECUTE,
                             phase_step.ASSERT__EXECUTE,
                             phase_step.CLEANUP
                             ],
                            True))

    def test_with_anonymous_phase_with_hard_error(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL)) \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatReturns(
                         sh.new_sh_hard_error('hard error msg')))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.new_without_step(phases.ANONYMOUS),
                                    test_case.the_extra(phases.ANONYMOUS)[1].first_line,
                                    'hard error msg'),
                            [phase_step.ANONYMOUS
                             ],
                            False))

    def test_with_implementation_error(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatSetsExecutionMode(ExecutionMode.XFAIL)) \
            .add(phases.CLEANUP,
                 test.CleanupPhaseInstructionWithImplementationError(
                         test.ImplementationErrorTestException()))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.new_without_step(phases.CLEANUP),
                                    test_case.the_extra(phases.CLEANUP)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.ANONYMOUS,
                             phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.ACT__SCRIPT_GENERATE,
                             phase_step.ACT__SCRIPT_VALIDATE,
                             phase_step.ACT__SCRIPT_EXECUTE,
                             phase_step.ASSERT__EXECUTE,
                             phase_step.CLEANUP
                             ],
                            True))


if __name__ == '__main__':
    unittest.main()
