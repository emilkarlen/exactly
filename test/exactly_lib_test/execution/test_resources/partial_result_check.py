import unittest

from exactly_lib.execution.partial_execution import PartialResultStatus, PartialResult
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_resources.expected_instruction_failure import ExpectedFailure, \
    ExpectedFailureForNoFailure


class ExpectedPartialResult:
    def __init__(self,
                 status: PartialResultStatus,
                 directory_structure: SandboxDirectoryStructure,
                 instruction_failure: ExpectedFailure):
        self.__status = status
        self.__sandbox_directory_structure = directory_structure
        self.__expected_instruction_failure = instruction_failure

    def assertions(self,
                   unittest_case: unittest.TestCase,
                   actual_result: PartialResult):
        unittest_case.assertEqual(self.__status,
                                  actual_result.status,
                                  'Status')
        unittest_case.assertEqual(self.__sandbox_directory_structure,
                                  actual_result.sandbox_directory_structure,
                                  'Sandbox directory structure')
        self.__expected_instruction_failure.assertions(unittest_case,
                                                       actual_result.failure_info)


def expected_pass(directory_structure: SandboxDirectoryStructure) -> ExpectedPartialResult:
    return ExpectedPartialResult(PartialResultStatus.PASS,
                                 directory_structure,
                                 ExpectedFailureForNoFailure())
