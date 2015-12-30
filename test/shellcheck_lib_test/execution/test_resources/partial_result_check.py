import unittest

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.execution.result import PartialResult
from shellcheck_lib.execution.partial_execution import PartialResultStatus, PartialResult
from shellcheck_lib_test.test_resources.expected_instruction_failure import ExpectedFailure, \
    ExpectedFailureForNoFailure


class ExpectedPartialResult:
    def __init__(self,
                 status: PartialResultStatus,
                 directory_structure: ExecutionDirectoryStructure,
                 instruction_failure: ExpectedFailure):
        self.__status = status
        self.__execution_directory_structure = directory_structure
        self.__expected_instruction_failure = instruction_failure

    def assertions(self,
                   unittest_case: unittest.TestCase,
                   actual_result: PartialResult):
        unittest_case.assertEqual(self.__status,
                                  actual_result.status,
                                  'Status')
        unittest_case.assertEqual(self.__execution_directory_structure,
                                  actual_result.execution_directory_structure,
                                  'Execution Directory Structure')
        self.__expected_instruction_failure.assertions(unittest_case,
                                                       actual_result.failure_info)


def expected_pass(directory_structure: ExecutionDirectoryStructure) -> ExpectedPartialResult:
    return ExpectedPartialResult(PartialResultStatus.PASS,
                                 directory_structure,
                                 ExpectedFailureForNoFailure())
