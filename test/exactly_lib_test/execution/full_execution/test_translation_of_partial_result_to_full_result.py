import unittest

from exactly_lib.execution.full_execution.result import FullExeResultStatus, translate_status
from exactly_lib.execution.partial_execution.result import PartialExeResultStatus
from exactly_lib.test_case.test_case_status import ExecutionMode


class Test(unittest.TestCase):
    def test_PASS(self):
        self.assertEqual(FullExeResultStatus.PASS,
                         translate_status(ExecutionMode.PASS,
                                          PartialExeResultStatus.PASS))

        self.assertEqual(FullExeResultStatus.FAIL,
                         translate_status(ExecutionMode.PASS,
                                          PartialExeResultStatus.FAIL))

        self.assertEqual(FullExeResultStatus.HARD_ERROR,
                         translate_status(ExecutionMode.PASS,
                                          PartialExeResultStatus.HARD_ERROR))

        self.assertEqual(FullExeResultStatus.IMPLEMENTATION_ERROR,
                         translate_status(ExecutionMode.PASS,
                                          PartialExeResultStatus.IMPLEMENTATION_ERROR))

    def test_FAIL(self):
        self.assertEqual(FullExeResultStatus.XPASS,
                         translate_status(ExecutionMode.FAIL,
                                          PartialExeResultStatus.PASS))

        self.assertEqual(FullExeResultStatus.XFAIL,
                         translate_status(ExecutionMode.FAIL,
                                          PartialExeResultStatus.FAIL))

        self.assertEqual(FullExeResultStatus.HARD_ERROR,
                         translate_status(ExecutionMode.FAIL,
                                          PartialExeResultStatus.HARD_ERROR))

        self.assertEqual(FullExeResultStatus.IMPLEMENTATION_ERROR,
                         translate_status(ExecutionMode.FAIL,
                                          PartialExeResultStatus.IMPLEMENTATION_ERROR))
