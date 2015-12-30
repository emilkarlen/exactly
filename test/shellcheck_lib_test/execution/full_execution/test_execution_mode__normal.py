import unittest

from shellcheck_lib.execution import phase_step, phases
from shellcheck_lib.execution.phase_step import PhaseStep
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.execution.full_execution.test_resources import instruction_test_resources
from shellcheck_lib_test.execution.full_execution.test_resources.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording, \
    TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList
from shellcheck_lib_test.execution.full_execution.test_resources.test_case_that_records_phase_execution import \
    new_test_case_with_recording, validate_action_that_raises, validate_action_that_returns, execute_action_that_raises
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailureForNoFailure, \
    ExpectedFailureForInstructionFailure, ExpectedFailureForPhaseFailure


class Test(unittest.TestCase):
    def test_full_sequence(self):
        new_test_case_with_recording(
            self,
            TestCaseGeneratorForExecutionRecording(),
            FullResultStatus.PASS,
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
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_hard_error_in_anonymous_phase(self):
        test_case_generator = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(instruction_test_resources.AnonymousPhaseInstructionThatReturns(
            sh.new_sh_hard_error('hard error msg')))
        new_test_case_with_recording(
            self,
            test_case_generator,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForInstructionFailure.new_with_message(
                phase_step.new_without_step(phases.ANONYMOUS),
                test_case_generator.the_anonymous_phase_extra[0].first_line,
                'hard error msg'),
            [phase_step.ANONYMOUS
             ],
            False).execute()

    def test_implementation_error_in_anonymous_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(
            instruction_test_resources.AnonymousPhaseInstructionWithImplementationError(
                instruction_test_resources.ImplementationErrorTestException()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedFailureForInstructionFailure.new_with_exception(
                PhaseStep(phases.ANONYMOUS, None),
                test_case.the_anonymous_phase_extra[0].first_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS
             ],
            False).execute()

    def test_validation_error_in_setup_validate_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionThatReturns(
                svh.new_svh_validation_error(
                    'validation error from setup/validate'),
                sh.new_sh_success(),
                svh.new_svh_success()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.VALIDATE,
            ExpectedFailureForInstructionFailure.new_with_message(
                PhaseStep(phases.SETUP, phase_step.PRE_VALIDATE),
                test_case.the_setup_phase_extra[0].first_line,
                'validation error from setup/validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             ],
            True).execute()

    def test_hard_error_in_setup_validate_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionThatReturns(
                svh.new_svh_hard_error('hard error from setup/validate'),
                sh.new_sh_success(),
                svh.new_svh_success()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForInstructionFailure.new_with_message(
                PhaseStep(phases.SETUP, phase_step.PRE_VALIDATE),
                test_case.the_setup_phase_extra[0].first_line,
                'hard error from setup/validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             ],
            True).execute()

    def test_implementation_error_in_setup_validate_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionWithImplementationErrorInPreValidate(
                instruction_test_resources.ImplementationErrorTestException()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedFailureForInstructionFailure.new_with_exception(
                PhaseStep(phases.SETUP, phase_step.PRE_VALIDATE),
                test_case.the_setup_phase_extra[0].first_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             ],
            True).execute()

    def test_hard_error_in_setup_execute_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionThatReturns(
                from_pre_validate=svh.new_svh_success(),
                from_execute=sh.new_sh_hard_error('hard error msg from setup'),
                from_post_validate=svh.new_svh_success()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForInstructionFailure.new_with_message(
                PhaseStep(phases.SETUP, phase_step.EXECUTE),
                test_case.the_setup_phase_extra[0].first_line,
                'hard error msg from setup'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_implementation_error_in_setup_execute_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionWithExceptionInExecute(
                instruction_test_resources.ImplementationErrorTestException()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedFailureForInstructionFailure.new_with_exception(
                PhaseStep(phases.SETUP, phase_step.EXECUTE),
                test_case.the_setup_phase_extra[0].first_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_validation_error_in_setup_post_validate_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionThatReturns(
                svh.new_svh_success(),
                sh.new_sh_success(),
                svh.new_svh_validation_error(
                    'validation error from setup/post-validate')))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.VALIDATE,
            ExpectedFailureForInstructionFailure.new_with_message(
                PhaseStep(phases.SETUP, phase_step.POST_VALIDATE),
                test_case.the_setup_phase_extra[0].first_line,
                'validation error from setup/post-validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_hard_error_in_setup_post_validate_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionThatReturns(
                svh.new_svh_success(),
                sh.new_sh_success(),
                svh.new_svh_hard_error('hard error from setup/post-validate')))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForInstructionFailure.new_with_message(
                PhaseStep(phases.SETUP, phase_step.POST_VALIDATE),
                test_case.the_setup_phase_extra[0].first_line,
                'hard error from setup/post-validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_implementation_error_in_setup_post_validate_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionWithImplementationErrorInPostValidate(
                instruction_test_resources.ImplementationErrorTestException()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedFailureForInstructionFailure.new_with_exception(
                PhaseStep(phases.SETUP, phase_step.POST_VALIDATE),
                test_case.the_setup_phase_extra[0].first_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_validation_error_in_assert_validate_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionThatReturns(
                from_validate=svh.new_svh_validation_error('ASSERT/validate'),
                from_execute=pfh.new_pfh_pass()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.VALIDATE,
            ExpectedFailureForInstructionFailure.new_with_message(
                PhaseStep(phases.ASSERT, phase_step.VALIDATE),
                test_case.the_assert_phase_extra[0].first_line,
                'ASSERT/validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_hard_error_in_assert_validate_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionThatReturns(
                from_validate=svh.new_svh_hard_error('ASSERT/validate'),
                from_execute=pfh.new_pfh_pass()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForInstructionFailure.new_with_message(
                PhaseStep(phases.ASSERT, phase_step.VALIDATE),
                test_case.the_assert_phase_extra[0].first_line,
                'ASSERT/validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_implementation_error_in_assert_validate_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionWithExceptionInValidate(
                instruction_test_resources.ImplementationErrorTestException()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedFailureForInstructionFailure.new_with_exception(
                PhaseStep(phases.ASSERT, phase_step.VALIDATE),
                test_case.the_assert_phase_extra[0].first_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_validation_error_in_act_validate_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_act(
            instruction_test_resources.ActPhaseInstructionThatReturns(
                from_validate=svh.new_svh_validation_error('ACT/validate'),
                from_execute=sh.new_sh_success()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.VALIDATE,
            ExpectedFailureForInstructionFailure.new_with_message(
                PhaseStep(phases.ACT, phase_step.VALIDATE),
                test_case.the_act_phase_extra[0].first_line,
                'ACT/validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_hard_error_in_act_validate_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_act(
            instruction_test_resources.ActPhaseInstructionThatReturns(
                from_validate=svh.new_svh_hard_error('ACT/validate'),
                from_execute=sh.new_sh_success()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForInstructionFailure.new_with_message(
                PhaseStep(phases.ACT, phase_step.VALIDATE),
                test_case.the_act_phase_extra[0].first_line,
                'ACT/validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_implementation_error_in_act_validate(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_act(
            instruction_test_resources.ActPhaseInstructionWithImplementationErrorInValidate(
                instruction_test_resources.ImplementationErrorTestException()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedFailureForInstructionFailure.new_with_exception(
                PhaseStep(phases.ACT, phase_step.VALIDATE),
                test_case.the_act_phase_extra[0].first_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_hard_error_in_act_script_generate(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_act(
            instruction_test_resources.ActPhaseInstructionThatReturns(
                from_validate=svh.new_svh_success(),
                from_execute=sh.new_sh_hard_error('hard error msg from act')))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForInstructionFailure.new_with_message(
                PhaseStep(phases.ACT, phase_step.ACT_script_generate),
                test_case.the_act_phase_extra[0].first_line,
                'hard error msg from act'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_implementation_error_in_act_script_generate(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_act(
            instruction_test_resources.ActPhaseInstructionWithImplementationErrorInExecute(
                instruction_test_resources.ImplementationErrorTestException()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedFailureForInstructionFailure.new_with_exception(
                PhaseStep(phases.ACT, phase_step.ACT_script_generate),
                test_case.the_act_phase_extra[0].first_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_validation_error_in_act_script_validate(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList()
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.VALIDATE,
            ExpectedFailureForPhaseFailure.new_with_message(
                PhaseStep(phases.ACT, phase_step.ACT_script_validate),
                'error message from validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATE,
             phase_step.ACT__SCRIPT_VALIDATE,
             phase_step.CLEANUP,
             ],
            True,
            validate_test_action=validate_action_that_returns(
                svh.new_svh_validation_error('error message from validate'))).execute()

    def test_hard_error_in_act_script_validate(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList()
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForPhaseFailure.new_with_message(
                PhaseStep(phases.ACT, phase_step.ACT_script_validate),
                'error message from validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATE,
             phase_step.ACT__SCRIPT_VALIDATE,
             phase_step.CLEANUP,
             ],
            True,
            validate_test_action=validate_action_that_returns(
                svh.new_svh_hard_error('error message from validate'))).execute()

    def test_implementation_error_in_act_script_validate(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList()
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedFailureForPhaseFailure.new_with_exception(
                PhaseStep(phases.ACT, phase_step.ACT_script_validate),
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATE,
             phase_step.ACT__SCRIPT_VALIDATE,
             phase_step.CLEANUP,
             ],
            True,
            validate_test_action=validate_action_that_raises(
                instruction_test_resources.ImplementationErrorTestException())).execute()

    def test_implementation_error_in_act_script_execute(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList()
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedFailureForPhaseFailure.new_with_exception(
                PhaseStep(phases.ACT, phase_step.ACT_script_execute),
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATE,
             phase_step.ACT__SCRIPT_VALIDATE,
             phase_step.ACT__SCRIPT_EXECUTE,
             phase_step.CLEANUP,
             ],
            True,
            execute_test_action=execute_action_that_raises(
                instruction_test_resources.ImplementationErrorTestException())).execute()

    def test_fail_in_assert_execute_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionThatReturns(
                from_validate=svh.new_svh_success(),
                from_execute=pfh.new_pfh_fail('fail msg from ASSERT')))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.FAIL,
            ExpectedFailureForInstructionFailure.new_with_message(
                PhaseStep(phases.ASSERT, phase_step.EXECUTE),
                test_case.the_assert_phase_extra[0].first_line,
                'fail msg from ASSERT'),
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
            True).execute()

    def test_hard_error_in_assert_execute_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionThatReturns(
                from_validate=svh.new_svh_success(),
                from_execute=pfh.new_pfh_hard_error('hard error msg from ASSERT')))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForInstructionFailure.new_with_message(
                PhaseStep(phases.ASSERT, phase_step.EXECUTE),
                test_case.the_assert_phase_extra[0].first_line,
                'hard error msg from ASSERT'),
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
            True).execute()

    def test_implementation_error_in_assert_execute_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionWithExceptionInExecute(
                instruction_test_resources.ImplementationErrorTestException()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedFailureForInstructionFailure.new_with_exception(
                PhaseStep(phases.ASSERT, phase_step.EXECUTE),
                test_case.the_assert_phase_extra[0].first_line,
                instruction_test_resources.ImplementationErrorTestException),
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
            True).execute()

    def test_hard_error_in_cleanup_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_cleanup(
            instruction_test_resources.CleanupPhaseInstructionThatReturns(
                sh.new_sh_hard_error('hard error msg from CLEANUP')))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForInstructionFailure.new_with_message(
                phase_step.new_without_step(phases.CLEANUP),
                test_case.the_cleanup_phase_extra[0].first_line,
                'hard error msg from CLEANUP'),
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
            True).execute()

    def test_implementation_error_in_cleanup_phase(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_cleanup(
            instruction_test_resources.CleanupPhaseInstructionWithImplementationError(
                instruction_test_resources.ImplementationErrorTestException()))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedFailureForInstructionFailure.new_with_exception(
                phase_step.new_without_step(phases.CLEANUP),
                test_case.the_cleanup_phase_extra[0].first_line,
                instruction_test_resources.ImplementationErrorTestException),
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
            True).execute()


if __name__ == '__main__':
    unittest.main()
