import unittest

from shelltest import phases
from shelltest.execution.phase_step import PhaseStep
from shelltest_test.execution.test_full_execution.util.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording, \
    TestCaseThatRecordsExecutionWithExtraInstructionList
from shelltest.execution.result import FullResultStatus
from shelltest.execution import phase_step
from shelltest_test.execution.test_full_execution.util.test_case_that_records_phase_execution import \
    TestCaseThatRecordsExecution
from shelltest_test.execution.util.expected_instruction_failure import ExpectedInstructionFailureForNoFailure, \
    ExpectedInstructionFailureForFailure
from shelltest_test.execution.test_full_execution.util import instruction_test_resources
from shelltest.test_case import pass_or_fail_or_hard_error_construction, \
    success_or_validation_hard_or_error_construction, \
    success_or_hard_error_construction


class Test(unittest.TestCase):
    def test_full_sequence(self):
        TestCaseThatRecordsExecution(
            self,
            TestCaseGeneratorForExecutionRecording(),
            FullResultStatus.PASS,
            ExpectedInstructionFailureForNoFailure(),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_hard_error_in_anonymous_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(instruction_test_resources.AnonymousPhaseInstructionThatReturnsHardError('hard error msg'))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                phase_step.new_without_step(phases.ANONYMOUS),
                test_case.the_anonymous_phase_extra[0].source_line,
                'hard error msg'),
            [phase_step.ANONYMOUS
             ],
            [],
            False).execute()

    def test_implementation_error_in_anonymous_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(
            instruction_test_resources.AnonymousPhaseInstructionWithImplementationError(
                instruction_test_resources.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                PhaseStep(phases.ANONYMOUS, None),
                test_case.the_anonymous_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS
             ],
            [],
            False).execute()

    def test_validation_error_in_setup_validate_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionThatReturns(
                success_or_validation_hard_or_error_construction.new_validation_error(
                    'validation error from setup/validate'),
                success_or_hard_error_construction.new_success(),
                success_or_validation_hard_or_error_construction.new_success()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.VALIDATE,
            ExpectedInstructionFailureForFailure.new_with_message(
                PhaseStep(phases.SETUP, phase_step.PRE_VALIDATE),
                test_case.the_setup_phase_extra[0].source_line,
                'validation error from setup/validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             ],
            [],
            True).execute()

    def test_hard_error_in_setup_validate_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionThatReturns(
                success_or_validation_hard_or_error_construction.new_hard_error('hard error from setup/validate'),
                success_or_hard_error_construction.new_success(),
                success_or_validation_hard_or_error_construction.new_success()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                PhaseStep(phases.SETUP, phase_step.PRE_VALIDATE),
                test_case.the_setup_phase_extra[0].source_line,
                'hard error from setup/validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             ],
            [],
            True).execute()

    def test_implementation_error_in_setup_validate_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionWithImplementationErrorInPreValidate(
                instruction_test_resources.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                PhaseStep(phases.SETUP, phase_step.PRE_VALIDATE),
                test_case.the_setup_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             ],
            [],
            True).execute()

    def test_hard_error_in_setup_execute_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionThatReturns(
                from_pre_validate=success_or_validation_hard_or_error_construction.new_success(),
                from_execute=success_or_hard_error_construction.new_hard_error('hard error msg from setup'),
                from_post_validate=success_or_validation_hard_or_error_construction.new_success()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                PhaseStep(phases.SETUP, phase_step.EXECUTE),
                test_case.the_setup_phase_extra[0].source_line,
                'hard error msg from setup'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_implementation_error_in_setup_execute_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionWithImplementationErrorInExecute(
                instruction_test_resources.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                PhaseStep(phases.SETUP, phase_step.EXECUTE),
                test_case.the_setup_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.CLEANUP,
             ],
            True).execute()


    def test_validation_error_in_setup_post_validate_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionThatReturns(
                success_or_validation_hard_or_error_construction.new_success(),
                success_or_hard_error_construction.new_success(),
                success_or_validation_hard_or_error_construction.new_validation_error(
                    'validation error from setup/post-validate')))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.VALIDATE,
            ExpectedInstructionFailureForFailure.new_with_message(
                PhaseStep(phases.SETUP, phase_step.POST_VALIDATE),
                test_case.the_setup_phase_extra[0].source_line,
                'validation error from setup/post-validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_hard_error_in_setup_post_validate_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionThatReturns(
                success_or_validation_hard_or_error_construction.new_success(),
                success_or_hard_error_construction.new_success(),
                success_or_validation_hard_or_error_construction.new_hard_error('hard error from setup/post-validate')))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                PhaseStep(phases.SETUP, phase_step.POST_VALIDATE),
                test_case.the_setup_phase_extra[0].source_line,
                'hard error from setup/post-validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_implementation_error_in_setup_post_validate_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionWithImplementationErrorInPostValidate(
                instruction_test_resources.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                PhaseStep(phases.SETUP, phase_step.POST_VALIDATE),
                test_case.the_setup_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_validation_error_in_assert_validate_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionThatReturns(
                from_validate=success_or_validation_hard_or_error_construction.new_validation_error('ASSERT/validate'),
                from_execute=success_or_hard_error_construction.new_success()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.VALIDATE,
            ExpectedInstructionFailureForFailure.new_with_message(
                PhaseStep(phases.ASSERT, phase_step.VALIDATE),
                test_case.the_assert_phase_extra[0].source_line,
                'ASSERT/validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_hard_error_in_assert_validate_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionThatReturns(
                from_validate=success_or_validation_hard_or_error_construction.new_hard_error('ASSERT/validate'),
                from_execute=success_or_hard_error_construction.new_success()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                PhaseStep(phases.ASSERT, phase_step.VALIDATE),
                test_case.the_assert_phase_extra[0].source_line,
                'ASSERT/validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_implementation_error_in_assert_validate_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionWithImplementationErrorInValidate(
                instruction_test_resources.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                PhaseStep(phases.ASSERT, phase_step.VALIDATE),
                test_case.the_assert_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_validation_error_in_act_validate_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_act(
            instruction_test_resources.ActPhaseInstructionThatReturns(
                from_validate=success_or_validation_hard_or_error_construction.new_validation_error('ACT/validate'),
                from_execute=success_or_hard_error_construction.new_success()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.VALIDATE,
            ExpectedInstructionFailureForFailure.new_with_message(
                PhaseStep(phases.ACT, phase_step.VALIDATE),
                test_case.the_act_phase_extra[0].source_line,
                'ACT/validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_hard_error_in_act_validate_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_act(
            instruction_test_resources.ActPhaseInstructionThatReturns(
                from_validate=success_or_validation_hard_or_error_construction.new_hard_error('ACT/validate'),
                from_execute=success_or_hard_error_construction.new_success()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                PhaseStep(phases.ACT, phase_step.VALIDATE),
                test_case.the_act_phase_extra[0].source_line,
                'ACT/validate'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_implementation_error_in_act_validate_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_act(
            instruction_test_resources.ActPhaseInstructionWithImplementationErrorInValidate(
                instruction_test_resources.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                PhaseStep(phases.ACT, phase_step.VALIDATE),
                test_case.the_act_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_hard_error_in_act_script_generation(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_act(
            instruction_test_resources.ActPhaseInstructionThatReturns(
                from_validate=success_or_validation_hard_or_error_construction.new_success(),
                from_execute=success_or_hard_error_construction.new_hard_error('hard error msg from act')))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                PhaseStep(phases.ACT, phase_step.ACT_script_generation),
                test_case.the_act_phase_extra[0].source_line,
                'hard error msg from act'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_implementation_error_in_act_script_generation(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_act(
            instruction_test_resources.ActPhaseInstructionWithImplementationErrorInExecute(
                instruction_test_resources.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                PhaseStep(phases.ACT, phase_step.ACT_script_generation),
                test_case.the_act_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.CLEANUP,
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.CLEANUP,
             ],
            True).execute()

    def test_fail_in_assert_execute_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionThatReturns(
                from_validate=success_or_validation_hard_or_error_construction.new_success(),
                from_execute=pass_or_fail_or_hard_error_construction.new_fail('fail msg from ASSERT')))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.FAIL,
            ExpectedInstructionFailureForFailure.new_with_message(
                PhaseStep(phases.ASSERT, phase_step.EXECUTE),
                test_case.the_assert_phase_extra[0].source_line,
                'fail msg from ASSERT'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            True).execute()

    def test_hard_error_in_assert_execute_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionThatReturns(
                from_validate=success_or_validation_hard_or_error_construction.new_success(),
                from_execute=pass_or_fail_or_hard_error_construction.new_hard_error('hard error msg from ASSERT')))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                PhaseStep(phases.ASSERT, phase_step.EXECUTE),
                test_case.the_assert_phase_extra[0].source_line,
                'hard error msg from ASSERT'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            True).execute()

    def test_implementation_error_in_assert_execute_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionWithImplementationErrorInExecute(
                instruction_test_resources.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                PhaseStep(phases.ASSERT, phase_step.EXECUTE),
                test_case.the_assert_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            True).execute()

    def test_hard_error_in_cleanup_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_cleanup(
            instruction_test_resources.CleanupPhaseInstructionThatReturnsHardError('hard error msg from CLEANUP'))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                phase_step.new_without_step(phases.CLEANUP),
                test_case.the_cleanup_phase_extra[0].source_line,
                'hard error msg from CLEANUP'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            True).execute()

    def test_implementation_error_in_cleanup_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_cleanup(
            instruction_test_resources.CleanupPhaseInstructionWithImplementationError(
                instruction_test_resources.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                phase_step.new_without_step(phases.CLEANUP),
                test_case.the_cleanup_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP__PRE_VALIDATE,
             phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            [phase_step.SETUP__EXECUTE,
             phase_step.SETUP__POST_VALIDATE,
             phase_step.ACT__VALIDATE,
             phase_step.ASSERT__VALIDATE,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT__EXECUTE,
             phase_step.CLEANUP
             ],
            True).execute()


if __name__ == '__main__':
    unittest.main()
