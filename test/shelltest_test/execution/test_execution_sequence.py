__author__ = 'emil'

import unittest

from shelltest_test.execution.util.test_case_that_records_phase_execution import \
    SETUP, ACT_SCRIPT_GENERATION, ACT_SCRIPT_EXECUTION,  CLEANUP, ASSERT
from shelltest_test.execution.util.test_case_that_records_phase_execution import \
    TestCaseThatRecordsExecutionWithSingleExtraInstruction


class Test(unittest.TestCase):
    def test_full_sequence(self):
        TestCaseThatRecordsExecutionWithSingleExtraInstruction(
            self,
            [ACT_SCRIPT_GENERATION,
             SETUP,
             ASSERT,
             CLEANUP],
            [SETUP,
             ACT_SCRIPT_EXECUTION,
             ASSERT,
             CLEANUP],
            True,
            None, None, None, None, None
        ).execute()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
