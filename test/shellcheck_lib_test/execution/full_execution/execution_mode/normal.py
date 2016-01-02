import unittest

from shellcheck_lib.execution import phase_step, phases
from shellcheck_lib.execution.phase_step import PhaseStep
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib_test.execution.full_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase, one_successful_instruction_in_each_phase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_EDS_VALIDATION_STEPS
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForNoFailure, \
    ExpectedFailureForInstructionFailure


class Test(TestCaseBase):
    def test_full_sequence(self):
        self._check(
                Arrangement(one_successful_instruction_in_each_phase()),
                Expectation(FullResultStatus.PASS,
                            ExpectedFailureForNoFailure(),
                            [phase_step.ANONYMOUS] +
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP__MAIN,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.ACT__SCRIPT_GENERATE,
                             phase_step.ACT__SCRIPT_VALIDATE,
                             phase_step.ACT__SCRIPT_EXECUTE,
                             phase_step.ASSERT__MAIN,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_hard_error_in_anonymous_phase(self):
        test_case_generator = one_successful_instruction_in_each_phase() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionThatReturns(
                         sh.new_sh_hard_error('hard error msg')))
        self._check(
                Arrangement(test_case_generator),
                Expectation(FullResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.new_without_step(phases.ANONYMOUS),
                                    test_case_generator.the_extra(phases.ANONYMOUS)[0].first_line,
                                    'hard error msg'),
                            [phase_step.ANONYMOUS],
                            False))

    def test_implementation_error_in_anonymous_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(phases.ANONYMOUS,
                 test.AnonymousPhaseInstructionWithImplementationError(
                         test.ImplementationErrorTestException()))
        self._check(
                Arrangement(test_case),
                Expectation(FullResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    PhaseStep(phases.ANONYMOUS, None),
                                    test_case.the_extra(phases.ANONYMOUS)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.ANONYMOUS],
                            False))


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
