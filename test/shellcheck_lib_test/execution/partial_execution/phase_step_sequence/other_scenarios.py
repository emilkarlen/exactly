import unittest

from shellcheck_lib.execution import phase_step
from shellcheck_lib.execution.result import PartialResultStatus
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.partial_execution.test_resources.recording.test_case_that_records_phase_execution import \
    Expectation, Arrangement, TestCaseBase, one_successful_instruction_in_each_phase
from shellcheck_lib_test.execution.partial_execution.test_resources.test_case_generator import PartialPhase
from shellcheck_lib_test.execution.test_resources import instruction_test_resources as test
from shellcheck_lib_test.execution.test_resources.execution_recording.phase_steps import PRE_EDS_VALIDATION_STEPS
from shellcheck_lib_test.execution.test_resources.instruction_test_resources import do_raise, do_return
from shellcheck_lib_test.execution.test_resources.test_actions import validate_action_that_returns, \
    validate_action_that_raises, execute_action_that_raises
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForInstructionFailure, \
    ExpectedFailureForPhaseFailure


class Test(TestCaseBase):
    def test_hard_error_in_setup_main_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.setup_phase_instruction_that(
                         main=do_return(sh.new_sh_hard_error('hard error msg from setup'))))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.SETUP_MAIN,
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    'hard error msg from setup'),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_implementation_error_in_setup_main_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.setup_phase_instruction_that(
                         main=do_raise(test.ImplementationErrorTestException())))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.SETUP_MAIN,
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    test.ImplementationErrorTestException),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_validation_error_in_setup_post_validate_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.setup_phase_instruction_that(
                         post_validate=test.do_return(svh.new_svh_validation_error(
                                 'validation error from setup/post-validate'))))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.VALIDATE,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.SETUP_POST_VALIDATE,
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    'validation error from setup/post-validate'),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_hard_error_in_setup_post_validate_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.setup_phase_instruction_that(
                         post_validate=do_return(svh.new_svh_hard_error('hard error from setup/post-validate'))))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.SETUP_POST_VALIDATE,
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    'hard error from setup/post-validate'),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_implementation_error_in_setup_post_validate_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.SETUP,
                 test.setup_phase_instruction_that(
                         post_validate=do_raise(test.ImplementationErrorTestException())))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.SETUP_POST_VALIDATE,
                                    test_case.the_extra(PartialPhase.SETUP)[0].first_line,
                                    test.ImplementationErrorTestException),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_validation_error_in_assert_validate_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that_returns(
                         from_validate=svh.new_svh_validation_error('ASSERT/validate')))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.VALIDATE,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ASSERT_VALIDATE_POST_EDS,
                                    test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                                    'ASSERT/validate'),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.ASSERT_VALIDATE_POST_EDS,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_hard_error_in_assert_validate_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that_returns(
                         from_validate=svh.new_svh_hard_error('ASSERT/validate')))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ASSERT_VALIDATE_POST_EDS,
                                    test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                                    'ASSERT/validate'),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.ASSERT_VALIDATE_POST_EDS,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_implementation_error_in_assert_validate_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that(
                         validate=test.do_raise(test.ImplementationErrorTestException())))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.ASSERT_VALIDATE_POST_EDS,
                                    test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                                    test.ImplementationErrorTestException),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.ASSERT_VALIDATE_POST_EDS,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_validation_error_in_act_validate_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ACT,
                 test.act_phase_instruction_that(
                         do_validate=do_return(svh.new_svh_validation_error('ACT/validate'))))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.VALIDATE,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ACT_VALIDATE_POST_EDS,
                                    test_case.the_extra(PartialPhase.ACT)[0].first_line,
                                    'ACT/validate'),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_hard_error_in_act_validate_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ACT,
                 test.act_phase_instruction_that(
                         do_validate=do_return(svh.new_svh_hard_error('ACT/validate'))))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ACT_VALIDATE_POST_EDS,
                                    test_case.the_extra(PartialPhase.ACT)[0].first_line,
                                    'ACT/validate'),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_implementation_error_in_act_validate(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ACT,
                 test.act_phase_instruction_that(
                         do_validate=do_raise(test.ImplementationErrorTestException())))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.ACT_VALIDATE_POST_EDS,
                                    test_case.the_extra(PartialPhase.ACT)[0].first_line,
                                    test.ImplementationErrorTestException),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_hard_error_in_act_script_generate(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ACT,
                 test.act_phase_instruction_that(
                         do_main=do_return(sh.new_sh_hard_error('hard error msg from act'))))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ACT_MAIN,
                                    test_case.the_extra(PartialPhase.ACT)[0].first_line,
                                    'hard error msg from act'),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.ASSERT_VALIDATE_POST_EDS,
                             phase_step.ACT_MAIN,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_implementation_error_in_act_script_generate(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ACT,
                 test.act_phase_instruction_that(
                         do_main=do_raise(test.ImplementationErrorTestException())))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.ACT_MAIN,
                                    test_case.the_extra(PartialPhase.ACT)[0].first_line,
                                    test.ImplementationErrorTestException),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.ASSERT_VALIDATE_POST_EDS,
                             phase_step.ACT_MAIN,
                             phase_step.CLEANUP_MAIN,
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
                                    phase_step.ACT_SCRIPT_VALIDATE,
                                    'error message from validate'),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.ASSERT_VALIDATE_POST_EDS,
                             phase_step.ACT_MAIN,
                             phase_step.ACT_SCRIPT_VALIDATE,
                             phase_step.CLEANUP_MAIN,
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
                                    phase_step.ACT_SCRIPT_VALIDATE,
                                    'error message from validate'),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.ASSERT_VALIDATE_POST_EDS,
                             phase_step.ACT_MAIN,
                             phase_step.ACT_SCRIPT_VALIDATE,
                             phase_step.CLEANUP_MAIN,
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
                                    phase_step.ACT_SCRIPT_VALIDATE,
                                    test.ImplementationErrorTestException),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.ASSERT_VALIDATE_POST_EDS,
                             phase_step.ACT_MAIN,
                             phase_step.ACT_SCRIPT_VALIDATE,
                             phase_step.CLEANUP_MAIN,
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
                                    phase_step.ACT_SCRIPT_EXECUTE,
                                    test.ImplementationErrorTestException),
                            PRE_EDS_VALIDATION_STEPS +
                            [phase_step.SETUP_MAIN,
                             phase_step.SETUP_POST_VALIDATE,
                             phase_step.ACT_VALIDATE_POST_EDS,
                             phase_step.ASSERT_VALIDATE_POST_EDS,
                             phase_step.ACT_MAIN,
                             phase_step.ACT_SCRIPT_VALIDATE,
                             phase_step.ACT_SCRIPT_EXECUTE,
                             phase_step.CLEANUP_MAIN,
                             ],
                            True))

    def test_fail_in_assert_main_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that_returns(
                         from_main=pfh.new_pfh_fail('fail msg from ASSERT')))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.FAIL,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ASSERT_MAIN,
                                    test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                                    'fail msg from ASSERT'),
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

    def test_hard_error_in_assert_main_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that_returns(
                         from_main=pfh.new_pfh_hard_error('hard error msg from ASSERT')))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.ASSERT_MAIN,
                                    test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                                    'hard error msg from ASSERT'),
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

    def test_implementation_error_in_assert_main_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.ASSERT,
                 test.assert_phase_instruction_that(
                         main=test.do_raise(test.ImplementationErrorTestException())))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.ASSERT_MAIN,
                                    test_case.the_extra(PartialPhase.ASSERT)[0].first_line,
                                    test.ImplementationErrorTestException),
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

    def test_hard_error_in_cleanup_main_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.CLEANUP,
                 test.cleanup_phase_instruction_that(
                         do_main=test.do_return(sh.new_sh_hard_error('hard error msg from CLEANUP'))))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.HARD_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_message(
                                    phase_step.CLEANUP_MAIN,
                                    test_case.the_extra(PartialPhase.CLEANUP)[0].first_line,
                                    'hard error msg from CLEANUP'),
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

    def test_implementation_error_in_cleanup_main_step(self):
        test_case = one_successful_instruction_in_each_phase() \
            .add(PartialPhase.CLEANUP,
                 test.cleanup_phase_instruction_that(
                         do_main=test.do_raise(test.ImplementationErrorTestException())))
        self._check(
                Arrangement(test_case),
                Expectation(PartialResultStatus.IMPLEMENTATION_ERROR,
                            ExpectedFailureForInstructionFailure.new_with_exception(
                                    phase_step.CLEANUP_MAIN,
                                    test_case.the_extra(PartialPhase.CLEANUP)[0].first_line,
                                    test.ImplementationErrorTestException),
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


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
