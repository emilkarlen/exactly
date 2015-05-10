from shelltest.exec_abs_syn import instructions
from shelltest.exec_abs_syn.success_or_hard_error_construction import new_success
from shelltest_test.execution.test_full_execution_sequence import instructions_with_errors

__author__ = 'emil'

import unittest

from shelltest_test.execution.test_full_execution_sequence.test_case_generation_for_sequence_tests import \
    TestCaseThatRecordsExecutionWithExtraInstructionList
from shelltest.execution.result import FullResultStatus
from shelltest.execution import phase_step
from shelltest_test.execution.test_full_execution_sequence.test_case_that_records_phase_execution import \
    TestCaseThatRecordsExecution
from shelltest_test.execution.util.expected_instruction_failure import ExpectedInstructionFailureForNoFailure, \
    ExpectedInstructionFailureForFailure


class AnonymousPhaseInstructionThatSetsExecutionMode(instructions.AnonymousPhaseInstruction):
    def __init__(self,
                 value_to_set: instructions.ExecutionMode):
        self.value_to_set = value_to_set

    def execute(self,
                phase_name: str,
                global_environment,
                phase_environment: instructions.PhaseEnvironmentForAnonymousPhase) -> instructions.SuccessOrHardError:
        phase_environment.set_execution_mode(self.value_to_set)
        return new_success()


class Test(unittest.TestCase):
    def test_execution_mode_skipped(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(instructions.ExecutionMode.SKIPPED))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.SKIPPED,
            ExpectedInstructionFailureForNoFailure(),
            [phase_step.ANONYMOUS
             ],
            [],
            False).execute()

    def test_execution_mode_skipped_but_failing_instruction_in_anonymous_phase_before_setting_execution_mode(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(instructions_with_errors.AnonymousPhaseInstructionThatReturnsHardError('hard error msg')) \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(instructions.ExecutionMode.SKIPPED))
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

    def test_execution_mode_skipped_but_failing_instruction_in_anonymous_phase_after_setting_execution_mode(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(instructions.ExecutionMode.SKIPPED)) \
            .add_anonymous(instructions_with_errors.AnonymousPhaseInstructionThatReturnsHardError('hard error msg'))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                test_case.the_anonymous_phase_extra[1].source_line,
                'hard error msg'),
            [phase_step.ANONYMOUS
             ],
            [],
            False).execute()


if __name__ == '__main__':
    unittest.main()
