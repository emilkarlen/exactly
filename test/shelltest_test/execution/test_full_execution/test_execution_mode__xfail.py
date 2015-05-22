import unittest

from shelltest import phases
from shelltest_test.execution.test_full_execution.util import instruction_test_resources
from shelltest_test.execution.test_full_execution.util.instruction_test_resources import \
    AnonymousPhaseInstructionThatSetsExecutionMode
from shelltest.test_case import instructions
from shelltest_test.execution.test_full_execution.util.test_case_generation_for_sequence_tests import \
    TestCaseThatRecordsExecutionWithExtraInstructionList
from shelltest.execution.result import FullResultStatus
from shelltest.execution import phase_step
from shelltest_test.execution.test_full_execution.util.test_case_that_records_phase_execution import \
    TestCaseThatRecordsExecution
from shelltest_test.execution.util.expected_instruction_failure import ExpectedInstructionFailureForFailure, \
    ExpectedInstructionFailureForNoFailure
from shelltest.test_case import pass_or_fail_or_hard_error_construction, \
    success_or_validation_hard_or_error_construction


class Test(unittest.TestCase):
    def test_with_assert_phase_that_fails(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(instructions.ExecutionMode.XFAIL)) \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionThatReturns(
                from_validate=success_or_validation_hard_or_error_construction.new_success(),
                from_execute=pass_or_fail_or_hard_error_construction.new_fail('fail message')))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.XFAIL,
            ExpectedInstructionFailureForFailure.new_with_message(
                phase_step.PhaseStep(phases.ASSERT, phase_step.EXECUTE),
                test_case.the_assert_phase_extra[0].source_line,
                'fail message'),
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
             phase_step.CLEANUP],
            True).execute()

    def test_with_assert_phase_that_passes(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(instructions.ExecutionMode.XFAIL))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.XPASS,
            ExpectedInstructionFailureForNoFailure(),
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
             phase_step.CLEANUP],
            True).execute()

    def test_with_anonymous_phase_with_hard_error(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(instructions.ExecutionMode.XFAIL)) \
            .add_anonymous(instruction_test_resources.AnonymousPhaseInstructionThatReturnsHardError('hard error msg'))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                phase_step.new_without_step(phases.ANONYMOUS),
                test_case.the_anonymous_phase_extra[1].source_line,
                'hard error msg'),
            [phase_step.ANONYMOUS
             ],
            [],
            False).execute()

    def test_with_implementation_error(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(instructions.ExecutionMode.XFAIL)) \
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
             phase_step.CLEANUP],
            True).execute()


if __name__ == '__main__':
    unittest.main()
