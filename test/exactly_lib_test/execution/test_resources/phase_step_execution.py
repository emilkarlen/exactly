from exactly_lib.execution.impl.phase_step_execution import ElementHeaderExecutor
from exactly_lib.execution.impl.single_instruction_executor import ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.util import line_source


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
    def __init__(self, name: str):
        self.name = name


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
