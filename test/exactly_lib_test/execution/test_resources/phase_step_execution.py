import unittest

from exactly_lib.execution.impl.phase_step_execution import ElementHeaderExecutor
from exactly_lib.execution.impl.result import Failure
from exactly_lib.execution.impl.single_instruction_executor import ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo
from exactly_lib.execution.partial_execution.result import PartialResultStatus
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.util import line_source
from exactly_lib.util.line_source import SourceLocationPath
from exactly_lib_test.test_resources.expected_instruction_failure import ExpectedFailureDetails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class ExpectedResult(tuple):
    def __new__(cls,
                status: PartialResultStatus,
                line: asrt.ValueAssertion[SourceLocationPath],
                failure_details: ExpectedFailureDetails):
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
            self.line.apply_with_message(unittest_case,
                                         return_value.source_location,
                                         'source location path')
            self.failure_details.assertions(unittest_case,
                                            return_value.failure_details,
                                            'Failure details')

    @property
    def status(self) -> PartialResultStatus:
        return self[0]

    @property
    def line(self) -> asrt.ValueAssertion[line_source.SourceLocationPath]:
        return self[1]

    @property
    def failure_details(self) -> ExpectedFailureDetails:
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


class TestInstruction(TestCaseInstruction):
    def __init__(self,
                 name: str):
        self.name = name

    @property
    def phase(self) -> phase_identifier.Phase:
        raise ValueError('should not be used in test')


class ElementHeaderExecutorThatRecordsHeaderAndLineNumber(ElementHeaderExecutor):
    def __init__(self,
                 recorder: Recorder):
        self.__recorder = recorder

    def apply(self, line: line_source.LineSequence):
        self.__recorder.record_header_value(str(line.first_line_number))


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
