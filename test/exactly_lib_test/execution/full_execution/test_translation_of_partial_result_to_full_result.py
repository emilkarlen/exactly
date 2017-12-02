import unittest

from exactly_lib.execution.full_execution import translate_status
from exactly_lib.execution.result import FullResultStatus, PartialResultStatus
from exactly_lib.test_case.test_case_status import ExecutionMode


class Test(unittest.TestCase):
    def test_PASS(self):
        self.assertEqual(FullResultStatus.PASS,
                         translate_status(ExecutionMode.PASS,
                                          PartialResultStatus.PASS))

        self.assertEqual(FullResultStatus.FAIL,
                         translate_status(ExecutionMode.PASS,
                                          PartialResultStatus.FAIL))

        self.assertEqual(FullResultStatus.HARD_ERROR,
                         translate_status(ExecutionMode.PASS,
                                          PartialResultStatus.HARD_ERROR))

        self.assertEqual(FullResultStatus.IMPLEMENTATION_ERROR,
                         translate_status(ExecutionMode.PASS,
                                          PartialResultStatus.IMPLEMENTATION_ERROR))

    def test_FAIL(self):
        self.assertEqual(FullResultStatus.XPASS,
                         translate_status(ExecutionMode.FAIL,
                                          PartialResultStatus.PASS))

        self.assertEqual(FullResultStatus.XFAIL,
                         translate_status(ExecutionMode.FAIL,
                                          PartialResultStatus.FAIL))

        self.assertEqual(FullResultStatus.HARD_ERROR,
                         translate_status(ExecutionMode.FAIL,
                                          PartialResultStatus.HARD_ERROR))

        self.assertEqual(FullResultStatus.IMPLEMENTATION_ERROR,
                         translate_status(ExecutionMode.FAIL,
                                          PartialResultStatus.IMPLEMENTATION_ERROR))
