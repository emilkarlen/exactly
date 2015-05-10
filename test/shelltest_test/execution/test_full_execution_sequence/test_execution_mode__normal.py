__author__ = 'emil'

import unittest

from shelltest_test.execution.test_full_execution_sequence.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording, \
    TestCaseThatRecordsExecutionWithExtraInstructionList
from shelltest.execution.result import FullResultStatus
from shelltest.execution import phase_step
from shelltest_test.execution.test_full_execution_sequence.test_case_that_records_phase_execution import \
    TestCaseThatRecordsExecution
from shelltest_test.execution.util.expected_instruction_failure import ExpectedInstructionFailureForNoFailure, \
    ExpectedInstructionFailureForFailure
from shelltest_test.execution.test_full_execution_sequence import instruction_test_resources


class Test(unittest.TestCase):
    def test_full_sequence(self):
        TestCaseThatRecordsExecution(
            self,
            TestCaseGeneratorForExecutionRecording(),
            FullResultStatus.PASS,
            ExpectedInstructionFailureForNoFailure(),
            [phase_step.ANONYMOUS,
             phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ASSERT,
             phase_step.CLEANUP
             ],
            [phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT,
             phase_step.CLEANUP],
            True).execute()

    def test_hard_error_in_anonymous_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(instruction_test_resources.AnonymousPhaseInstructionThatReturnsHardError('hard error msg'))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
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
                test_case.the_anonymous_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS
             ],
            [],
            False).execute()

    def test_hard_error_in_setup_execute_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionThatReturnsHardError('hard error msg from setup'))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                test_case.the_setup_phase_extra[0].source_line,
                'hard error msg from setup'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP
             ],
            [phase_step.SETUP],
            True).execute()

    def test_implementation_error_in_setup_execute_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(
            instruction_test_resources.SetupPhaseInstructionWithImplementationError(
                instruction_test_resources.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                test_case.the_setup_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP
             ],
            [phase_step.SETUP],
            True).execute()

    def test_hard_error_in_act_script_generation(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_act(instruction_test_resources.ActPhaseInstructionThatReturnsHardError('hard error msg from act'))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                test_case.the_act_phase_extra[0].source_line,
                'hard error msg from act'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION
             ],
            [phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION],
            True).execute()

    def test_implementation_error_in_act_script_generation(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_act(
            instruction_test_resources.ActPhaseInstructionWithImplementationError(
                instruction_test_resources.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                test_case.the_act_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION
             ],
            [phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION],
            True).execute()

    def test_fail_in_assert_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionThatReturnsFail('fail msg from ASSERT'))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.FAIL,
            ExpectedInstructionFailureForFailure.new_with_message(
                test_case.the_assert_phase_extra[0].source_line,
                'fail msg from ASSERT'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ASSERT,
             phase_step.CLEANUP
             ],
            [phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT,
             phase_step.CLEANUP
             ],
            True).execute()

    def test_hard_error_in_assert_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionThatReturnsHardError('hard error msg from ASSERT'))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                test_case.the_assert_phase_extra[0].source_line,
                'hard error msg from ASSERT'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ASSERT,
             phase_step.CLEANUP
             ],
            [phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT,
             phase_step.CLEANUP
             ],
            True).execute()

    def test_implementation_error_in_assert_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_assert(
            instruction_test_resources.AssertPhaseInstructionWithImplementationError(
                instruction_test_resources.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                test_case.the_assert_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ASSERT,
             phase_step.CLEANUP
             ],
            [phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT,
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
                test_case.the_cleanup_phase_extra[0].source_line,
                'hard error msg from CLEANUP'),
            [phase_step.ANONYMOUS,
             phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ASSERT,
             phase_step.CLEANUP
             ],
            [phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT,
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
                test_case.the_cleanup_phase_extra[0].source_line,
                instruction_test_resources.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ASSERT,
             phase_step.CLEANUP
             ],
            [phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT,
             phase_step.CLEANUP
             ],
            True).execute()


if __name__ == '__main__':
    unittest.main()
