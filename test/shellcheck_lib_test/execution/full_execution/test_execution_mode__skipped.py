import unittest

from shellcheck_lib.test_case.instruction.sections.anonymous import ExecutionMode
from shellcheck_lib_test.execution.full_execution.util import instruction_test_resources
from shellcheck_lib_test.execution.full_execution.util.instruction_test_resources import \
    AnonymousPhaseInstructionThatSetsExecutionMode
from shellcheck_lib_test.execution.full_execution.util.test_case_generation_for_sequence_tests import \
    TestCaseThatRecordsExecutionWithExtraInstructionList
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.execution import phase_step, phases
from shellcheck_lib_test.execution.full_execution.util.test_case_that_records_phase_execution import \
    TestCaseThatRecordsExecution
from shellcheck_lib_test.util.expected_instruction_failure import ExpectedInstructionFailureForNoFailure, \
    ExpectedInstructionFailureForFailure


class Test(unittest.TestCase):
    def test_execution_mode_skipped(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(
            ExecutionMode.SKIPPED))
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
            .add_anonymous(instruction_test_resources.AnonymousPhaseInstructionThatReturnsHardError('hard error msg')) \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(
            ExecutionMode.SKIPPED))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                phase_step.new_without_step(phases.ANONYMOUS),
                test_case.the_anonymous_phase_extra[0].first_line,
                'hard error msg'),
            [phase_step.ANONYMOUS
             ],
            [],
            False).execute()

    def test_execution_mode_skipped_but_failing_instruction_in_anonymous_phase_after_setting_execution_mode(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(
            ExecutionMode.SKIPPED)) \
            .add_anonymous(instruction_test_resources.AnonymousPhaseInstructionThatReturnsHardError('hard error msg'))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                phase_step.new_without_step(phases.ANONYMOUS),
                test_case.the_anonymous_phase_extra[1].first_line,
                'hard error msg'),
            [phase_step.ANONYMOUS
             ],
            [],
            False).execute()


if __name__ == '__main__':
    unittest.main()
