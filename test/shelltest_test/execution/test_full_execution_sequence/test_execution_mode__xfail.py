__author__ = 'emil'

import unittest

from shelltest_test.execution.test_full_execution_sequence.instruction_test_resources import \
    AnonymousPhaseInstructionThatSetsExecutionMode, AssertPhaseInstructionThatReturnsFail
from shelltest.exec_abs_syn import instructions
from shelltest_test.execution.test_full_execution_sequence.test_case_generation_for_sequence_tests import \
    TestCaseThatRecordsExecutionWithExtraInstructionList
from shelltest.execution.result import FullResultStatus
from shelltest.execution import phase_step
from shelltest_test.execution.test_full_execution_sequence.test_case_that_records_phase_execution import \
    TestCaseThatRecordsExecution
from shelltest_test.execution.util.expected_instruction_failure import ExpectedInstructionFailureForFailure


class Test(unittest.TestCase):
    def test_with_assert_phase_that_fails(self):
        test_case = TestCaseThatRecordsExecutionWithExtraInstructionList() \
            .add_anonymous(AnonymousPhaseInstructionThatSetsExecutionMode(instructions.ExecutionMode.XFAIL)) \
            .add_assert(AssertPhaseInstructionThatReturnsFail('fail message'))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.XFAIL,
            ExpectedInstructionFailureForFailure.new_with_message(
                test_case.the_assert_phase_extra[0].source_line,
                'fail message'),
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


if __name__ == '__main__':
    unittest.main()
