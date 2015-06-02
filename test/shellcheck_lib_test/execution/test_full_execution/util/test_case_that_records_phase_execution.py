import unittest

from shellcheck_lib.test_case import test_case_struct
from shellcheck_lib_test.execution.test_full_execution.util.test_case_base import FullExecutionTestCaseBase
from shellcheck_lib_test.util.expected_instruction_failure import ExpectedInstructionFailureBase
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib_test.execution.test_full_execution.util.recording_instructions_for_sequence_tests import \
    record_file_path
from shellcheck_lib_test.execution.test_full_execution.util.recording_instructions_for_sequence_tests import \
    record_file_contents_from_lines
from shellcheck_lib_test.execution.test_full_execution.util.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording


class TestCaseThatRecordsExecution(FullExecutionTestCaseBase):
    """
    Base class for tests on a test case that uses the Python 3 language in the apply phase.
    """

    def __init__(self,
                 unittest_case: unittest.TestCase,
                 test_case_generator: TestCaseGeneratorForExecutionRecording,
                 expected_status: FullResultStatus,
                 expected_failure_info: ExpectedInstructionFailureBase,
                 expected_internal_recording: list,
                 expected_file_recording: list,
                 execution_directory_structure_should_exist: bool,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case, dbg_do_not_delete_dir_structure)
        self._test_case_generator = test_case_generator
        self.__expected_status = expected_status
        self.__expected_failure_info = expected_failure_info
        self.__expected_internal_instruction_recording = expected_internal_recording
        self.__expected_file_recording = expected_file_recording
        self.__execution_directory_structure_should_exist = execution_directory_structure_should_exist

    def _test_case(self) -> test_case_struct.TestCase:
        return self._test_case_generator.test_case

    def _assertions(self):
        self.utc.assertEqual(self.__expected_status,
                             self.full_result.status,
                             'Unexpected result status')
        self.__expected_failure_info.assertions(self.utc,
                                                self.full_result.instruction_failure_info)
        msg = 'Difference in the sequence of executed phases and steps that are executed internally'
        self.utc.assertEqual(self.__expected_internal_instruction_recording,
                             self._test_case_generator.internal_instruction_recorder,
                             msg)
        if self.__execution_directory_structure_should_exist:
            self.utc.assertIsNotNone(self.eds)
            self.utc.assertTrue(
                self.eds.root_dir.is_dir(),
                'Execution Directory Structure root is expected to be a directory')
            file_path = record_file_path(self.eds)
            if not self.__expected_file_recording:
                self.utc.assertFalse(file_path.exists())
            else:
                expected_file_contents = record_file_contents_from_lines(self.__expected_file_recording)
                msg = 'Difference in sequence of phases/steps that are executed after Execution Directory Structure' + \
                      ' is created (recorded in file)'
                self.assert_is_regular_file_with_contents(file_path,
                                                          expected_file_contents,
                                                          msg)
        else:
            self.utc.assertIsNone(self.eds,
                                  'Execution Directory Structure is expected to not be created')
