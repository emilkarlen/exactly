import unittest

from shellcheck_lib.execution import phase_step, phases
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case.sections.anonymous import ExecutionMode
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib_test.execution.full_execution.test_resources import instruction_test_resources
from shellcheck_lib_test.execution.full_execution.test_resources.instruction_test_resources import \
    AnonymousPhaseInstructionThatSetsExecutionMode
from shellcheck_lib_test.execution.full_execution.test_resources.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList
from shellcheck_lib_test.execution.full_execution.test_resources.test_case_that_records_phase_execution import \
    new_test_case_with_recording
from shellcheck_lib_test.util.expected_instruction_failure import ExpectedFailureForNoFailure, \
    ExpectedFailureForInstructionFailure


class Test(unittest.TestCase):
    def test_execution_mode_skipped(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(
            ExecutionMode.SKIPPED))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.SKIPPED,
            ExpectedFailureForNoFailure(),
            [phase_step.ANONYMOUS
             ],
            False).execute()

    def test_execution_mode_skipped_but_failing_instruction_in_anonymous_phase_before_setting_execution_mode(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(instruction_test_resources.AnonymousPhaseInstructionThatReturns(
            sh.new_sh_hard_error('hard error msg'))) \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(
            ExecutionMode.SKIPPED))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForInstructionFailure.new_with_message(
                phase_step.new_without_step(phases.ANONYMOUS),
                test_case.the_anonymous_phase_extra[0].first_line,
                'hard error msg'),
            [phase_step.ANONYMOUS
             ],
            False).execute()

    def test_execution_mode_skipped_but_failing_instruction_in_anonymous_phase_after_setting_execution_mode(self):
        test_case = TestCaseGeneratorThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(
            ExecutionMode.SKIPPED)) \
            .add_anonymous(instruction_test_resources.AnonymousPhaseInstructionThatReturns(
            sh.new_sh_hard_error('hard error msg')))
        new_test_case_with_recording(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedFailureForInstructionFailure.new_with_message(
                phase_step.new_without_step(phases.ANONYMOUS),
                test_case.the_anonymous_phase_extra[1].first_line,
                'hard error msg'),
            [phase_step.ANONYMOUS
             ],
            False).execute()

        if __name__ == '__main__':
            unittest.main()
