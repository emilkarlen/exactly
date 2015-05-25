import unittest

from shelltest.execution.phase_step_execution import Failure, ElementHeaderExecutor
from shelltest.execution.result import PartialResultStatus
from shelltest.execution.single_instruction_executor import ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo
from shelltest.general import line_source
from shelltest.document.model import Instruction
from shelltest_test.execution.util.expected_instruction_failure import ExpectedInstructionFailureDetails
from shelltest_test.document.test_resources import assert_equals_line


class ExpectedResult(tuple):
    def __new__(cls,
                status: PartialResultStatus,
                line: line_source.Line,
                failure_details: ExpectedInstructionFailureDetails):
        return tuple.__new__(cls, (status,
                                   line,
                                   failure_details))

    def assertions(self,
                   unittest_case: unittest.TestCase,
                   return_value: Failure):
        if self.status is PartialResultStatus.PASS:
            unittest_case.assertIsNone(return_value,
                                       'Return value must be None (representing success)')
        else:
            unittest_case.assertIsNotNone(return_value,
                                          'Return value must not be None (representing failure)')
            unittest_case.assertEqual(self.status,
                                      return_value.status,
                                      'Status')
            assert_equals_line(unittest_case,
                               self.line,
                               return_value.source_line,
                               'Source Line')
            self.failure_details.assertions(unittest_case,
                                            return_value.failure_details,
                                            'Failure details')

    @property
    def status(self) -> PartialResultStatus:
        return self[0]

    @property
    def line(self) -> line_source.Line:
        return self[1]

    @property
    def failure_details(self) -> ExpectedInstructionFailureDetails:
        return self[2]


def expected_success() -> ExpectedResult:
    return ExpectedResult(PartialResultStatus.PASS,
                          None,
                          None)


class Recorder:
    def __init__(self,
                 output: list,
                 header: str):
        self.__list = output
        self.__header = header

    def record_header(self):
        self.__list.append(self.__header)

    def record_header_value(self, value: str):
        self.__list.append('%s: %s' % (self.__header, value))


class RecordingMedia:
    def __init__(self):
        self.__output = []

    @property
    def output(self) -> list:
        return self.__output

    def new_recorder_with_header(self, header: str) -> Recorder:
        return Recorder(self.__output,
                        header)


class TestInstruction(Instruction):
    def __init__(self,
                 name: str):
        self.name = name


class ElementHeaderExecutorThatRecordsHeaderAndLineNumber(ElementHeaderExecutor):
    def __init__(self,
                 recorder: Recorder):
        self.__recorder = recorder

    def apply(self, line: line_source.Line):
        self.__recorder.record_header_value(str(line.line_number))


class InstructionExecutorThatRecordsInstructionNameAndReturnsSuccess(ControlledInstructionExecutor):
    def __init__(self,
                 recorder: Recorder):
        self.__recorder = recorder

    def apply(self, instruction: TestInstruction) -> PartialInstructionControlledFailureInfo:
        self.__recorder.record_header_value(instruction.name)
        return None


class InstructionExecutorThatRecordsInstructionNameAndFailsFor(ControlledInstructionExecutor):
    def __init__(self,
                 record_name_matcher_for_instruction_that_should_fail,
                 recorder: Recorder,
                 ret_val: PartialInstructionControlledFailureInfo):
        self.__record_name_matcher = record_name_matcher_for_instruction_that_should_fail
        self.__recorder = recorder
        self.__ret_val = ret_val

    def apply(self, instruction: TestInstruction) -> PartialInstructionControlledFailureInfo:
        self.__recorder.record_header_value(instruction.name)
        if self.__record_name_matcher(instruction.name):
            return self.__ret_val
        return None


class TestException(Exception):
    pass


class InstructionExecutorThatRecordsInstructionNameAndRaisesExceptionFor(ControlledInstructionExecutor):
    def __init__(self,
                 record_name_matcher_for_instruction_that_should_fail,
                 recorder: Recorder,
                 exception: Exception):
        self.__record_name_matcher = record_name_matcher_for_instruction_that_should_fail
        self.__recorder = recorder
        self.__exception = exception

    def apply(self, instruction: TestInstruction) -> PartialInstructionControlledFailureInfo:
        self.__recorder.record_header_value(instruction.name)
        if self.__record_name_matcher(instruction.name):
            raise self.__exception
        return None


any_instruction = lambda name: True


def instruction_with_name(expected_name: str):
    return lambda actual_name: expected_name == actual_name
