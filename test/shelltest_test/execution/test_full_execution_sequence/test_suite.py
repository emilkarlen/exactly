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
from shelltest_test.execution.test_full_execution_sequence import instructions_with_errors


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
            .add_anonymous(instructions_with_errors.AnonymousPhaseInstructionThatReturnsHardError('hard error msg'))
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
            instructions_with_errors.AnonymousPhaseInstructionWithImplementationError(
                instructions_with_errors.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                test_case.the_anonymous_phase_extra[0].source_line,
                instructions_with_errors.ImplementationErrorTestException),
            [phase_step.ANONYMOUS
             ],
            [],
            False).execute()

    def test_hard_error_in_setup_execute_phase(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_setup(instructions_with_errors.SetupPhaseInstructionThatReturnsHardError('hard error msg from setup'))
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
            instructions_with_errors.SetupPhaseInstructionWithImplementationError(
                instructions_with_errors.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                test_case.the_setup_phase_extra[0].source_line,
                instructions_with_errors.ImplementationErrorTestException),
            [phase_step.ANONYMOUS,
             phase_step.SETUP
             ],
            [phase_step.SETUP],
            True).execute()

    def test_hard_error_in_act_script_generation(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_act(instructions_with_errors.ActPhaseInstructionThatReturnsHardError('hard error msg from act'))
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
            instructions_with_errors.ActPhaseInstructionWithImplementationError(
                instructions_with_errors.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                test_case.the_act_phase_extra[0].source_line,
                instructions_with_errors.ImplementationErrorTestException),
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
            instructions_with_errors.AssertPhaseInstructionThatReturnsFail('fail msg from ASSERT'))
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
            instructions_with_errors.AssertPhaseInstructionThatReturnsHardError('hard error msg from ASSERT'))
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
            instructions_with_errors.AssertPhaseInstructionWithImplementationError(
                instructions_with_errors.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                test_case.the_assert_phase_extra[0].source_line,
                instructions_with_errors.ImplementationErrorTestException),
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
            instructions_with_errors.CleanupPhaseInstructionThatReturnsHardError('hard error msg from CLEANUP'))
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
            instructions_with_errors.CleanupPhaseInstructionWithImplementationError(
                instructions_with_errors.ImplementationErrorTestException()))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.IMPLEMENTATION_ERROR,
            ExpectedInstructionFailureForFailure.new_with_exception(
                test_case.the_cleanup_phase_extra[0].source_line,
                instructions_with_errors.ImplementationErrorTestException),
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


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
