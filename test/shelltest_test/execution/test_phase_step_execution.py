from shelltest.phase_instr.line_source import Line
from shelltest_test.phase_instr.test_resources import assert_equals_line

__author__ = 'emil'

import unittest

from shelltest_test.execution.util.expected_instruction_failure import ExpectedInstructionFailureDetails, \
    new_expected_failure_message, new_expected_exception
from shelltest.execution.phase_step_execution import ElementHeaderExecutor, execute_phase_prim, Failure
from shelltest.execution.result import PartialResultStatus
from shelltest.phase_instr import line_source
from shelltest.phase_instr.model import Instruction, PhaseContentElement, PhaseContents, new_comment_element, \
    new_instruction_element
from shelltest.execution.single_instruction_executor import ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum


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


class Test(unittest.TestCase):
    def test_when_there_are_no_elements_no_executor_should_be_invoked_and_the_result_should_be_pass(self):
        phase_contents = PhaseContents(())
        self._standard_test_with_successful_instruction_executor(
            phase_contents,
            expected_success(),
            [])

    def test_when_there_are_only_comment_elements_than_the_result_should_be_pass(self):
        phase_contents = PhaseContents((new_comment_element(Line(1, '1')),
                                        new_comment_element(Line(2, '2'))))
        self._standard_test_with_successful_instruction_executor(
            phase_contents,
            expected_success(),
            ['comment header for source line number: 1',
             'comment header for source line number: 2'])

    def test_successful_execution_of_single_instruction(self):
        phase_contents = PhaseContents((new_instruction_element(Line(1, '1'),
                                                                TestInstruction('The instruction')),
                                        ))
        self._standard_test_with_successful_instruction_executor(
            phase_contents,
            expected_success(),
            ['instruction header for source line number: 1',
             'instruction executor: The instruction'])

    def test_successful_sequence(self):
        phase_contents = PhaseContents((new_instruction_element(Line(1, '1'),
                                                                TestInstruction('First instruction')),
                                        new_comment_element(Line(2, '2')),
                                        new_instruction_element(Line(3, '3'),
                                                                TestInstruction('Second instruction')),
                                        new_comment_element(Line(4, '4')),
                                        new_comment_element(Line(5, '5')),
                                        new_instruction_element(Line(6, '6'),
                                                                TestInstruction('Third instruction')),
                                        new_instruction_element(Line(7, '7'),
                                                                TestInstruction('Fourth instruction')),
                                        new_comment_element(Line(8, '8')),
                                        ))
        self._standard_test_with_successful_instruction_executor(
            phase_contents,
            expected_success(),
            ['instruction header for source line number: 1',
             'instruction executor: First instruction',

             'comment header for source line number: 2',

             'instruction header for source line number: 3',
             'instruction executor: Second instruction',

             'comment header for source line number: 4',

             'comment header for source line number: 5',

             'instruction header for source line number: 6',
             'instruction executor: Third instruction',

             'instruction header for source line number: 7',
             'instruction executor: Fourth instruction',

             'comment header for source line number: 8',
             ])

    def test_single_failing_instruction_executor__status_fail(self):
        recording_media = RecordingMedia()
        instruction_executor = InstructionExecutorThatRecordsInstructionNameAndFailsFor(
            any_instruction,
            recording_media.new_recorder_with_header('instruction executor'),
            PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.FAIL,
                                                    'fail message')
        )
        phase_contents = PhaseContents((new_instruction_element(Line(1, '1'),
                                                                TestInstruction('The instruction')),
                                        ))
        self._standard_test(
            recording_media,
            phase_contents,
            instruction_executor,
            ExpectedResult(PartialResultStatus.FAIL,
                           Line(1, '1'),
                           new_expected_failure_message('fail message')),
            ['instruction header for source line number: 1',
             'instruction executor: The instruction'])

    def test_single_failing_instruction_executor__status_hard_error(self):
        recording_media = RecordingMedia()
        instruction_executor = InstructionExecutorThatRecordsInstructionNameAndFailsFor(
            any_instruction,
            recording_media.new_recorder_with_header('instruction executor'),
            PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.HARD_ERROR,
                                                    'hard error message')
        )
        phase_contents = PhaseContents((new_instruction_element(Line(1, '1'),
                                                                TestInstruction('The instruction')),
                                        ))
        self._standard_test(
            recording_media,
            phase_contents,
            instruction_executor,
            ExpectedResult(PartialResultStatus.HARD_ERROR,
                           Line(1, '1'),
                           new_expected_failure_message('hard error message')),
            ['instruction header for source line number: 1',
             'instruction executor: The instruction'])

    def test_single_exception_raising_instruction_executor(self):
        recording_media = RecordingMedia()
        instruction_executor = InstructionExecutorThatRecordsInstructionNameAndRaisesExceptionFor(
            any_instruction,
            recording_media.new_recorder_with_header('instruction executor'),
            TestException()
        )
        phase_contents = PhaseContents((new_instruction_element(Line(1, '1'),
                                                                TestInstruction('The instruction')),
                                        ))
        self._standard_test(
            recording_media,
            phase_contents,
            instruction_executor,
            ExpectedResult(PartialResultStatus.IMPLEMENTATION_ERROR,
                           Line(1, '1'),
                           new_expected_exception(TestException)),
            ['instruction header for source line number: 1',
             'instruction executor: The instruction'])

    def _standard_test_with_successful_instruction_executor(self,
                                                            phase_contents: PhaseContents,
                                                            expected_result: ExpectedResult,
                                                            expected_recordings: list):
        recording_media = RecordingMedia()
        instruction_executor = InstructionExecutorThatRecordsInstructionNameAndReturnsSuccess(
            recording_media.new_recorder_with_header('instruction executor'))
        failure = self._run_std(recording_media,
                                phase_contents,
                                instruction_executor)
        self.__check(
            expected_result,
            failure,
            expected_recordings,
            recording_media)

    def _standard_test(self,
                       recording_media: RecordingMedia,
                       phase_contents: PhaseContents,
                       instruction_executor: ControlledInstructionExecutor,
                       expected_result: ExpectedResult,
                       expected_recordings: list):
        failure = self._run_std(recording_media,
                                phase_contents,
                                instruction_executor)
        self.__check(
            expected_result,
            failure,
            expected_recordings,
            recording_media)

    def _run_std(self,
                 recording_media: RecordingMedia,
                 phase_contents: PhaseContents,
                 instruction_executor: ControlledInstructionExecutor) -> Failure:
        return execute_phase_prim(
            phase_contents,
            ElementHeaderExecutorThatRecordsHeaderAndLineNumber(
                recording_media.new_recorder_with_header('comment header for source line number')),
            ElementHeaderExecutorThatRecordsHeaderAndLineNumber(
                recording_media.new_recorder_with_header('instruction header for source line number')),
            instruction_executor)

    def __check(self,
                expected_result: ExpectedResult,
                actual_result: Failure,
                expected_recordings: list,
                actual_recording_media: RecordingMedia):
        expected_result.assertions(self,
                                   actual_result)
        self.assertEqual(expected_recordings,
                         actual_recording_media.output,
                         'Recorded executions')


def new_dummy_instruction_element() -> PhaseContentElement:
    return PhaseContentElement(line_source.Line(100, '100'),
                               Instruction())


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
