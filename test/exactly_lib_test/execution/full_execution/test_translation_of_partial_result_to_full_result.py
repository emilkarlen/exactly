import unittest

from exactly_lib.execution.full_execution.result import FullExeResultStatus, translate_status
from exactly_lib.execution.partial_execution.result import PartialExeResultStatus
from exactly_lib.test_case.test_case_status import TestCaseStatus


class Test(unittest.TestCase):
    def test_PASS(self):
        self.assertEqual(FullExeResultStatus.PASS,
                         translate_status(TestCaseStatus.PASS,
                                          PartialExeResultStatus.PASS))

        self.assertEqual(FullExeResultStatus.FAIL,
                         translate_status(TestCaseStatus.PASS,
                                          PartialExeResultStatus.FAIL))

        self.assertEqual(FullExeResultStatus.HARD_ERROR,
                         translate_status(TestCaseStatus.PASS,
                                          PartialExeResultStatus.HARD_ERROR))

        self.assertEqual(FullExeResultStatus.IMPLEMENTATION_ERROR,
                         translate_status(TestCaseStatus.PASS,
                                          PartialExeResultStatus.IMPLEMENTATION_ERROR))

    def test_FAIL(self):
        self.assertEqual(FullExeResultStatus.XPASS,
                         translate_status(TestCaseStatus.FAIL,
                                          PartialExeResultStatus.PASS))

        self.assertEqual(FullExeResultStatus.XFAIL,
                         translate_status(TestCaseStatus.FAIL,
                                          PartialExeResultStatus.FAIL))

        self.assertEqual(FullExeResultStatus.HARD_ERROR,
                         translate_status(TestCaseStatus.FAIL,
                                          PartialExeResultStatus.HARD_ERROR))

        self.assertEqual(FullExeResultStatus.IMPLEMENTATION_ERROR,
                         translate_status(TestCaseStatus.FAIL,
                                          PartialExeResultStatus.IMPLEMENTATION_ERROR))
