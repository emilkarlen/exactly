import unittest

from exactly_lib.execution.partial_execution.result import PartialResultStatus, PartialResult
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.execution.test_resources.expected_instruction_failure import ExpectedFailure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


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
                                  actual_result.sds,
                                  'Sandbox directory structure')
        self.__expected_instruction_failure.assertions(unittest_case,
                                                       actual_result.failure_info)


def partial_result_status_is(expected: PartialResultStatus) -> asrt.ValueAssertion:
    return asrt.is_instance_with(PartialResult,
                                 asrt.sub_component('status',
                                                    PartialResult.status.fget,
                                                    asrt.equals(expected)))