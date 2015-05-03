__author__ = 'emil'

import os
import shutil
import pathlib
import unittest

from shelltest.execution.result import FullResultStatus, InstructionFailureInfo
from shelltest.phase_instr import model
from shelltest.phase_instr import line_source
from shelltest.script_language import python3
from shelltest.execution import execution
from shelltest_test.execution.util import utils
from shelltest_test.execution.test_execution_sequence.recording_instructions_for_sequence_tests import record_file_path
from shelltest_test.execution.test_execution_sequence.recording_instructions_for_sequence_tests import \
    record_file_contents_from_lines
from shelltest_test.execution.test_execution_sequence.test_case_generation_for_sequence_tests import \
    TestCaseGeneratorForExecutionRecording


class ExpectedInstructionFailureBase:
    def assertions(self,
                   unittest_case: unittest.TestCase,
                   actual_failure_info: InstructionFailureInfo):
        raise NotImplementedError()


class ExpectedInstructionFailureForNoFailure(ExpectedInstructionFailureBase):
    def assertions(self,
                   unittest_case: unittest.TestCase,
                   actual_failure_info: InstructionFailureInfo):
        unittest_case.assertIsNone(actual_failure_info,
                                   'There should be no failure')


class ExpectedInstructionFailureForFailure(ExpectedInstructionFailureBase, tuple):
    def __new__(cls,
                source_line: line_source.Line,
                error_message_or_none: str,
                exception_class_or_none):
        return tuple.__new__(cls, (source_line,
                                   error_message_or_none,
                                   exception_class_or_none))

    @staticmethod
    def new_with_message(source_line: line_source.Line,
                         error_message: str):
        return ExpectedInstructionFailureForFailure(source_line,
                                                    error_message,
                                                    None)

    @staticmethod
    def new_with_exception(source_line: line_source.Line,
                           exception_class):
        return ExpectedInstructionFailureForFailure(source_line,
                                                    None,
                                                    exception_class)

    def assertions(self,
                   unittest_case: unittest.TestCase,
                   actual_failure_info: InstructionFailureInfo):
        if actual_failure_info is not None:
            unittest_case.assertEqual(self.source_line.line_number,
                                      actual_failure_info.source_line.line_number,
                                      'Source line number')
            unittest_case.assertEqual(self.source_line.text,
                                      actual_failure_info.source_line.text,
                                      'Source text')
            if self.error_message_or_none is not None:
                unittest_case.assertIsNotNone(actual_failure_info.failure_details.error_message,
                                              'An error message is expected (not an exception)')
                unittest_case.assertEqual(actual_failure_info.failure_details.error_message,
                                          self.error_message_or_none,
                                          'Error message text')
            else:
                unittest_case.assertIsNotNone(actual_failure_info.failure_details.exception,
                                              'An exception is expected (not an error message)')
                unittest_case.assertIsInstance(actual_failure_info.failure_details.exception,
                                               self.exception_class_or_none,
                                               'Exception class')

    @property
    def source_line(self) -> line_source.Line:
        return self[0]

    @property
    def error_message_or_none(self) -> str:
        return self[1]

    @property
    def exception_class_or_none(self):
        return self[2]


class TestCaseThatRecordsExecution:
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
        self.__unittest_case = unittest_case
        self._test_case_generator = test_case_generator
        self.__previous_line_number = 0
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__expected_status = expected_status
        self.__expected_failure_info = expected_failure_info
        self.__expected_internal_instruction_recording = expected_internal_recording
        self.__expected_file_recording = expected_file_recording
        self.__execution_directory_structure_should_exist = execution_directory_structure_should_exist

        self.__full_result = None
        self.__execution_directory_structure = None

    def execute(self):
        # ARRANGE #
        home_dir_path = pathlib.Path().resolve()
        # ACT #
        full_result = execution.execute(
            python3.Python3ScriptFileManager(),
            python3.new_script_source_writer(),
            self._test_case_generator.test_case,
            home_dir_path,
            'shelltest-test-',
            True)

        # ASSERT #
        self.__full_result = full_result
        self._standard_assertions()
        self._custom_assertions()
        # CLEANUP #
        os.chdir(str(home_dir_path))
        if not self.__dbg_do_not_delete_dir_structure and self.eds:
            shutil.rmtree(str(self.eds.root_dir))
        else:
            if self.eds:
                print(str(self.eds.root_dir))

    def _next_line(self) -> line_source.Line:
        """
        Generates lines in a continuous sequence.
        """
        self.__previous_line_number += 1
        return line_source.Line(self.__previous_line_number,
                                str(self.__previous_line_number))

    def _next_instruction_line(self, instruction: model.Instruction) -> model.PhaseContentElement:
        return model.new_instruction_element(
            self._next_line(),
            instruction)

    def _standard_assertions(self):
        self.unittest_case.assertEqual(self.__expected_status,
                                       self.__full_result.status,
                                       'Unexpected result status')
        self.__expected_failure_info.assertions(self.unittest_case,
                                                self.__full_result.instruction_failure_info)
        msg = 'Difference in the sequence of executed phases and steps that are executed internally'
        self.unittest_case.assertEqual(self.__expected_internal_instruction_recording,
                                       self._test_case_generator.internal_instruction_recorder,
                                       msg)
        if self.__execution_directory_structure_should_exist:
            self.__unittest_case.assertIsNotNone(self.eds)
            self.__unittest_case.assertTrue(
                self.eds.root_dir.is_dir(),
                'Execution Directory Structure root is expected to be a directory')
            file_path = record_file_path(self.eds)
            if not self.__expected_file_recording:
                self.__unittest_case.assertFalse(file_path.exists())
            else:
                expected_file_contents = record_file_contents_from_lines(self.__expected_file_recording)
                msg = 'Difference in sequence of phases/steps that are executed after Execution Directory Structure' + \
                      ' is created (recorded in file)'
                self.assert_is_regular_file_with_contents(file_path,
                                                          expected_file_contents,
                                                          msg)
        else:
            self.__unittest_case.assertIsNone(self.eds,
                                              'Execution Directory Structure is expected to not be created')

    def _custom_assertions(self):
        pass

    @property
    def unittest_case(self) -> unittest.TestCase:
        return self.__unittest_case

    @property
    def eds(self) -> execution.ExecutionDirectoryStructure:
        return self.__full_result.execution_directory_structure

    def assert_is_regular_file_with_contents(self,
                                             path: pathlib.Path,
                                             expected_contents: str,
                                             msg=None):
        """
        Helper for test cases that check the contents of files.
        """
        utils.assert_is_file_with_contents(self.unittest_case,
                                           path,
                                           expected_contents,
                                           msg)
