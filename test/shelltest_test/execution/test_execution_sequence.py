__author__ = 'emil'

import unittest

from shelltest_test.execution.util.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording, \
    TestCaseThatRecordsExecutionWithSingleExtraInstruction
from shelltest.execution.result import FullResultStatus

from shelltest.execution import phase_step
from shelltest_test.execution.util.test_case_that_records_phase_execution import TestCaseThatRecordsExecution, \
    ExpectedInstructionFailureForNoFailure, ExpectedInstructionFailureForFailure
from shelltest_test.execution.sequence_test_cases import anonymous_phase_errors


class Test(unittest.TestCase):
    def test_full_sequence(self):
        TestCaseThatRecordsExecution(
            self,
            TestCaseGeneratorForExecutionRecording(),
            FullResultStatus.PASS,
            ExpectedInstructionFailureForNoFailure(),
            [phase_step.ANONYMOUS,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.SETUP,
             phase_step.ASSERT,
             phase_step.CLEANUP],
            [phase_step.SETUP,
             phase_step.ACT__SCRIPT_GENERATION,
             phase_step.ACT__SCRIPT_EXECUTION,
             phase_step.ASSERT,
             phase_step.CLEANUP],
            True).execute()

    def test_hard_error_in_anonymous_phase(self):
        test_case = TestCaseThatRecordsExecutionWithSingleExtraInstruction(
            anonymous_extra=anonymous_phase_errors.AnonymousPhaseInstructionThatReturnsHardError('hard error msg'))
        TestCaseThatRecordsExecution(
            self,
            test_case,
            FullResultStatus.HARD_ERROR,
            ExpectedInstructionFailureForFailure.new_with_message(
                test_case.the_anonymous_phase_extra.source_line,
                'hard error msg'),
            [phase_step.ANONYMOUS],
            [],
            False).execute()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
