import unittest

from exactly_lib.execution.full_execution.result import FullExeResultStatus, translate_status
from exactly_lib.execution.result import ExecutionFailureStatus
from exactly_lib.test_case.test_case_status import TestCaseStatus


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_PASS(self):
        self.assertEqual(FullExeResultStatus.PASS,
                         translate_status(TestCaseStatus.PASS,
                                          None))

        self.assertEqual(FullExeResultStatus.FAIL,
                         translate_status(TestCaseStatus.PASS,
                                          ExecutionFailureStatus.FAIL))

        self.assertEqual(FullExeResultStatus.HARD_ERROR,
                         translate_status(TestCaseStatus.PASS,
                                          ExecutionFailureStatus.HARD_ERROR))

        self.assertEqual(FullExeResultStatus.INTERNAL_ERROR,
                         translate_status(TestCaseStatus.PASS,
                                          ExecutionFailureStatus.INTERNAL_ERROR))

    def test_FAIL(self):
        self.assertEqual(FullExeResultStatus.XPASS,
                         translate_status(TestCaseStatus.FAIL,
                                          None))

        self.assertEqual(FullExeResultStatus.XFAIL,
                         translate_status(TestCaseStatus.FAIL,
                                          ExecutionFailureStatus.FAIL))

        self.assertEqual(FullExeResultStatus.HARD_ERROR,
                         translate_status(TestCaseStatus.FAIL,
                                          ExecutionFailureStatus.HARD_ERROR))

        self.assertEqual(FullExeResultStatus.INTERNAL_ERROR,
                         translate_status(TestCaseStatus.FAIL,
                                          ExecutionFailureStatus.INTERNAL_ERROR))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
