from shelltest.execution.result import FullResultStatus

__author__ = 'emil'

import unittest

from shelltest.execution import phase_step
from shelltest_test.execution.util.test_case_that_records_phase_execution import \
    TestCaseThatRecordsExecutionWithSingleExtraInstruction


class Test(unittest.TestCase):
    def test_full_sequence(self):
        TestCaseThatRecordsExecutionWithSingleExtraInstruction(
            self,
            FullResultStatus.PASS,
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
            True,
            None, None, None, None, None
        ).execute()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
