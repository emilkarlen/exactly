import unittest

from shelltest.exec_abs_syn.instructions import ExecutionMode
from shelltest.execution.full_execution import translate_status
from shelltest.execution.result import FullResultStatus, PartialResultStatus


class Test(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(FullResultStatus.PASS,
                         translate_status(ExecutionMode.NORMAL,
                                          PartialResultStatus.PASS))

        self.assertEqual(FullResultStatus.FAIL,
                         translate_status(ExecutionMode.NORMAL,
                                          PartialResultStatus.FAIL))

        self.assertEqual(FullResultStatus.HARD_ERROR,
                         translate_status(ExecutionMode.NORMAL,
                                          PartialResultStatus.HARD_ERROR))

        self.assertEqual(FullResultStatus.IMPLEMENTATION_ERROR,
                         translate_status(ExecutionMode.NORMAL,
                                          PartialResultStatus.IMPLEMENTATION_ERROR))

    def test_xfail(self):
        self.assertEqual(FullResultStatus.XPASS,
                         translate_status(ExecutionMode.XFAIL,
                                          PartialResultStatus.PASS))

        self.assertEqual(FullResultStatus.XFAIL,
                         translate_status(ExecutionMode.XFAIL,
                                          PartialResultStatus.FAIL))

        self.assertEqual(FullResultStatus.HARD_ERROR,
                         translate_status(ExecutionMode.XFAIL,
                                          PartialResultStatus.HARD_ERROR))

        self.assertEqual(FullResultStatus.IMPLEMENTATION_ERROR,
                         translate_status(ExecutionMode.XFAIL,
                                          PartialResultStatus.IMPLEMENTATION_ERROR))
