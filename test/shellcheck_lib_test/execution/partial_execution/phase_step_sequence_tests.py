import unittest

from shellcheck_lib.execution import phase_step, phases
from shellcheck_lib.execution.phase_step import PhaseStep
from shellcheck_lib.execution.result import PartialResultStatus
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase, one_successful_instruction_in_each_phase
from shellcheck_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.execution.test_resources.test_actions import validate_action_that_returns, \
    validate_action_that_raises, execute_action_that_raises
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForNoFailure, \
    ExpectedFailureForInstructionFailure, ExpectedFailureForPhaseFailure


class Test(TestCaseBase):
    def test_full_sequence(self):
        self._check(
                Arrangement(one_successful_instruction_in_each_phase()),
                Expectation(PartialResultStatus.PASS,
                            ExpectedFailureForNoFailure(),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.ACT__SCRIPT_GENERATE,
                             phase_step.ACT__SCRIPT_VALIDATE,
                             phase_step.ACT__SCRIPT_EXECUTE,
                             phase_step.ASSERT__EXECUTE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_validation_error_in_setup_validate_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.SetupPhaseInstructionThatReturns(
                         svh.new_svh_validation_error(
                                 'validation error from setup/validate'),
                         sh.new_sh_success(),
                         svh.new_svh_success()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.VALIDATE,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    PhaseStep(phases.SETUP, phase_step.PRE_VALIDATE),
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    'validation error from setup/validate'),
                            [phase_step.SETUP__PRE_VALIDATE,
                             ],
                            True))

    def test_hard_error_in_setup_validate_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.SetupPhaseInstructionThatReturns(
                         svh.new_svh_hard_error('hard error from setup/validate'),
                         sh.new_sh_success(),
                         svh.new_svh_success()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    PhaseStep(phases.SETUP, phase_step.PRE_VALIDATE),
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    'hard error from setup/validate'),
                            [phase_step.SETUP__PRE_VALIDATE,
                             ],
                            True))

    def test_implementation_error_in_setup_validate_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.SetupPhaseInstructionWithImplementationErrorInPreValidate(
                         test.ImplementationErrorTestException()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    PhaseStep(phases.SETUP, phase_step.PRE_VALIDATE),
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.SETUP__PRE_VALIDATE,
                             ],
                            True))

    def test_hard_error_in_setup_execute_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.SetupPhaseInstructionThatReturns(
                         from_pre_validate=svh.new_svh_success(),
                         from_execute=sh.new_sh_hard_error('hard error msg from setup'),
                         from_post_validate=svh.new_svh_success()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    PhaseStep(phases.SETUP, phase_step.EXECUTE),
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    'hard error msg from setup'),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_implementation_error_in_setup_execute_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.SetupPhaseInstructionWithExceptionInExecute(
                         test.ImplementationErrorTestException()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    PhaseStep(phases.SETUP, phase_step.EXECUTE),
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_validation_error_in_setup_post_validate_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.SetupPhaseInstructionThatReturns(
                         svh.new_svh_success(),
                         sh.new_sh_success(),
                         svh.new_svh_validation_error(
                                 'validation error from setup/post-validate')))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.VALIDATE,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    PhaseStep(phases.SETUP, phase_step.POST_VALIDATE),
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    'validation error from setup/post-validate'),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_hard_error_in_setup_post_validate_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.SetupPhaseInstructionThatReturns(
                         svh.new_svh_success(),
                         sh.new_sh_success(),
                         svh.new_svh_hard_error('hard error from setup/post-validate')))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    PhaseStep(phases.SETUP, phase_step.POST_VALIDATE),
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    'hard error from setup/post-validate'),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_implementation_error_in_setup_post_validate_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.SetupPhaseInstructionWithImplementationErrorInPostValidate(
                         test.ImplementationErrorTestException()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    PhaseStep(phases.SETUP, phase_step.POST_VALIDATE),
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_validation_error_in_assert_validate_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ASSERT,
                 test.AssertPhaseInstructionThatReturns(
                         from_validate=svh.new_svh_validation_error('ASSERT/validate'),
                         from_execute=pfh.new_pfh_pass()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.VALIDATE,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    PhaseStep(phases.ASSERT, phase_step.VALIDATE),
                                    test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                                    'ASSERT/validate'),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_hard_error_in_assert_validate_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ASSERT,
                 test.AssertPhaseInstructionThatReturns(
                         from_validate=svh.new_svh_hard_error('ASSERT/validate'),
                         from_execute=pfh.new_pfh_pass()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    PhaseStep(phases.ASSERT, phase_step.VALIDATE),
                                    test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                                    'ASSERT/validate'),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_implementation_error_in_assert_validate_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ASSERT,
                 test.AssertPhaseInstructionWithExceptionInValidate(
                         test.ImplementationErrorTestException()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    PhaseStep(phases.ASSERT, phase_step.VALIDATE),
                                    test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_validation_error_in_act_validate_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ACT,
                 test.ActPhaseInstructionThatReturns(
                         from_validate=svh.new_svh_validation_error('ACT/validate'),
                         from_execute=sh.new_sh_success()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.VALIDATE,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    PhaseStep(phases.ACT, phase_step.VALIDATE),
                                    test_case.the_extra(PartialPhase.ACT)[0].first_line,
                                    'ACT/validate'),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_hard_error_in_act_validate_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ACT,
                 test.ActPhaseInstructionThatReturns(
                         from_validate=svh.new_svh_hard_error('ACT/validate'),
                         from_execute=sh.new_sh_success()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    PhaseStep(phases.ACT, phase_step.VALIDATE),
                                    test_case.the_extra(PartialPhase.ACT)[0].first_line,
                                    'ACT/validate'),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_implementation_error_in_act_validate(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ACT,
                 test.ActPhaseInstructionWithImplementationErrorInValidate(
                         test.ImplementationErrorTestException()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    PhaseStep(phases.ACT, phase_step.VALIDATE),
                                    test_case.the_extra(PartialPhase.ACT)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_hard_error_in_act_script_generate(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ACT,
                 test.ActPhaseInstructionThatReturns(
                         from_validate=svh.new_svh_success(),
                         from_execute=sh.new_sh_hard_error('hard error msg from act')))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    PhaseStep(phases.ACT, phase_step.ACT_script_generate),
                                    test_case.the_extra(PartialPhase.ACT)[0].first_line,
                                    'hard error msg from act'),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.ACT__SCRIPT_GENERATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_implementation_error_in_act_script_generate(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ACT,
                 test.ActPhaseInstructionWithImplementationErrorInExecute(
                         test.ImplementationErrorTestException()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    PhaseStep(phases.ACT, phase_step.ACT_script_generate),
                                    test_case.the_extra(PartialPhase.ACT)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.ACT__SCRIPT_GENERATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_validation_error_in_act_script_validate(self):
        test_case = one_successful_instruction_in_each_phase()
        self._check(
                Arrangement(test_case,
                            validate_test_action=validate_action_that_returns(
                                    svh.new_svh_validation_error('error message from validate'))),
                Expectation(PartialResultStatus.VALIDATE,
                            ExpectedFailureForPhaseFailure.new_with_message(
                                    PhaseStep(phases.ACT, phase_step.ACT_script_validate),
                                    'error message from validate'),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.ACT__SCRIPT_GENERATE,
                             phase_step.ACT__SCRIPT_VALIDATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_hard_error_in_act_script_validate(self):
        test_case = one_successful_instruction_in_each_phase()
        self._check(
                Arrangement(test_case,
                            validate_test_action=validate_action_that_returns(
                                    svh.new_svh_hard_error('error message from validate'))),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForPhaseFailure.new_with_message(
                                    PhaseStep(phases.ACT, phase_step.ACT_script_validate),
                                    'error message from validate'),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.ACT__SCRIPT_GENERATE,
                             phase_step.ACT__SCRIPT_VALIDATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_implementation_error_in_act_script_validate(self):
        test_case = one_successful_instruction_in_each_phase()
        self._check(
                Arrangement(test_case,
                            validate_test_action=validate_action_that_raises(
                                    test.ImplementationErrorTestException())),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForPhaseFailure.new_with_exception(
                                    PhaseStep(phases.ACT, phase_step.ACT_script_validate),
                                    test.ImplementationErrorTestException),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.ACT__SCRIPT_GENERATE,
                             phase_step.ACT__SCRIPT_VALIDATE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_implementation_error_in_act_script_execute(self):
        test_case = one_successful_instruction_in_each_phase()
        self._check(
                Arrangement(test_case,
                            execute_test_action=execute_action_that_raises(
                                    test.ImplementationErrorTestException())),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForPhaseFailure.new_with_exception(
                                    PhaseStep(phases.ACT, phase_step.ACT_script_execute),
                                    test.ImplementationErrorTestException),
                            [phase_step.SETUP__PRE_VALIDATE,
                             phase_step.SETUP__EXECUTE,
                             phase_step.SETUP__POST_VALIDATE,
                             phase_step.ACT__VALIDATE,
                             phase_step.ASSERT__VALIDATE,
                             phase_step.ACT__SCRIPT_GENERATE,
                             phase_step.ACT__SCRIPT_VALIDATE,
                             phase_step.ACT__SCRIPT_EXECUTE,
                             phase_step.CLEANUP,
                             ],
                            True))

    def test_fail_in_assert_execute_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ASSERT,
                 test.AssertPhaseInstructionThatReturns(
                         from_validate=svh.new_svh_success(),
                         from_execute=pfh.new_pfh_fail('fail msg from ASSERT')))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.FAIL,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    PhaseStep(phases.ASSERT, phase_step.EXECUTE),
                                    test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                                    'fail msg from ASSERT'),
                            [phase_step.SETUP__PRE_VALIDATE,
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

    def test_hard_error_in_assert_execute_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ASSERT,
                 test.AssertPhaseInstructionThatReturns(
                         from_validate=svh.new_svh_success(),
                         from_execute=pfh.new_pfh_hard_error('hard error msg from ASSERT')))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    PhaseStep(phases.ASSERT, phase_step.EXECUTE),
                                    test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                                    'hard error msg from ASSERT'),
                            [phase_step.SETUP__PRE_VALIDATE,
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

    def test_implementation_error_in_assert_execute_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ASSERT,
                 test.AssertPhaseInstructionWithExceptionInExecute(
                         test.ImplementationErrorTestException()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    PhaseStep(phases.ASSERT, phase_step.EXECUTE),
                                    test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.SETUP__PRE_VALIDATE,
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

    def test_hard_error_in_cleanup_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.CLEANUP,
                 test.CleanupPhaseInstructionThatReturns(
                         sh.new_sh_hard_error('hard error msg from CLEANUP')))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.CLEANUP_EXECUTE,
                                    test_case.the_extra(PartialPhase.CLEANUP)[0].first_line,
                                    'hard error msg from CLEANUP'),
                            [phase_step.SETUP__PRE_VALIDATE,
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

    def test_implementation_error_in_cleanup_phase(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.CLEANUP,
                 test.CleanupPhaseInstructionWithImplementationError(
                         test.ImplementationErrorTestException()))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.CLEANUP_EXECUTE,
                                    test_case.the_extra(PartialPhase.CLEANUP)[0].first_line,
                                    test.ImplementationErrorTestException),
                            [phase_step.SETUP__PRE_VALIDATE,
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


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
