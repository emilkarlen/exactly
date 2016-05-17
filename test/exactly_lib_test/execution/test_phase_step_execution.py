import unittest

from exactly_lib.execution.phase_step_execution import execute_phase_prim, Failure
from exactly_lib.execution.result import PartialResultStatus
from exactly_lib.execution.single_instruction_executor import ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum
from exactly_lib.section_document.model import SectionContents
from exactly_lib.util.line_source import Line
from exactly_lib_test.execution.test_resources.phase_step_execution import ExpectedResult, expected_success, \
    RecordingMedia, \
    TestInstruction, ElementHeaderExecutorThatRecordsHeaderAndLineNumber, \
    InstructionExecutorThatRecordsInstructionNameAndReturnsSuccess, \
    InstructionExecutorThatRecordsInstructionNameAndFailsFor, TestException, \
    InstructionExecutorThatRecordsInstructionNameAndRaisesExceptionFor, any_instruction, instruction_with_name
from exactly_lib_test.test_resources.expected_instruction_failure import \
    new_expected_failure_message, \
    new_expected_exception
from exactly_lib_test.test_resources.model_utils import new_comment_element, new_instruction_element


class Test(unittest.TestCase):
    def test_when_there_are_no_elements_no_executor_should_be_invoked_and_the_result_should_be_pass(self):
        phase_contents = SectionContents(())
        self._standard_test_with_successful_instruction_executor(
            phase_contents,
            expected_success(),
            [])

    def test_when_there_are_only_comment_elements_than_the_result_should_be_pass(self):
        phase_contents = SectionContents((new_comment_element(Line(1, '1')),
                                          new_comment_element(Line(2, '2'))))
        self._standard_test_with_successful_instruction_executor(
            phase_contents,
            expected_success(),
            ['comment header for source line number: 1',
             'comment header for source line number: 2'])

    def test_successful_execution_of_single_instruction(self):
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
                                                                  TestInstruction('The instruction')),
                                          ))
        self._standard_test_with_successful_instruction_executor(
            phase_contents,
            expected_success(),
            ['instruction header for source line number: 1',
             'instruction executor: The instruction'])

    def test_successful_sequence(self):
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
                                                                  TestInstruction('First instruction')),
                                          new_comment_element(Line(2, '2')),
                                          new_instruction_element(Line(3, '3'),
                                                                TestInstruction('Second instruction')),
                                          new_comment_element(Line(4, '4')),
                                          new_comment_element(Line(50, '50')),
                                          new_instruction_element(Line(60, '60'),
                                                                TestInstruction('Third instruction')),
                                          new_instruction_element(Line(70, '70'),
                                                                  TestInstruction('Fourth instruction')),
                                          new_comment_element(Line(80, '80')),
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

             'comment header for source line number: 50',

             'instruction header for source line number: 60',
             'instruction executor: Third instruction',

             'instruction header for source line number: 70',
             'instruction executor: Fourth instruction',

             'comment header for source line number: 80',
             ])

    def test_single_failing_instruction_executor__status_fail(self):
        recording_media = RecordingMedia()
        instruction_executor = InstructionExecutorThatRecordsInstructionNameAndFailsFor(
            any_instruction,
            recording_media.new_recorder_with_header('instruction executor'),
            PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.FAIL,
                                                    'fail message')
        )
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
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
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
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
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
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

    def test_first_instruction_fails(self):
        recording_media = RecordingMedia()
        instruction_executor = InstructionExecutorThatRecordsInstructionNameAndFailsFor(
            instruction_with_name('First instruction'),
            recording_media.new_recorder_with_header('instruction executor'),
            PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.FAIL,
                                                    'fail message')
        )
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
                                                                  TestInstruction('First instruction')),
                                          new_instruction_element(Line(2, '2'),
                                                                TestInstruction('Second instruction'))
                                          ))
        self._standard_test(
            recording_media,
            phase_contents,
            instruction_executor,
            ExpectedResult(PartialResultStatus.FAIL,
                           Line(1, '1'),
                           new_expected_failure_message('fail message')),
            ['instruction header for source line number: 1',
             'instruction executor: First instruction'])

    def test_middle_instruction_fails(self):
        recording_media = RecordingMedia()
        instruction_executor = InstructionExecutorThatRecordsInstructionNameAndFailsFor(
            instruction_with_name('Middle instruction'),
            recording_media.new_recorder_with_header('instruction executor'),
            PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.FAIL,
                                                    'fail message')
        )
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
                                                                  TestInstruction('First instruction')),
                                          new_instruction_element(Line(2, '2'),
                                                                TestInstruction('Middle instruction')),
                                          new_instruction_element(Line(3, '3'),
                                                                  TestInstruction('Last instruction')),
                                          ))
        self._standard_test(
            recording_media,
            phase_contents,
            instruction_executor,
            ExpectedResult(PartialResultStatus.FAIL,
                           Line(2, '2'),
                           new_expected_failure_message('fail message')),
            ['instruction header for source line number: 1',
             'instruction executor: First instruction',
             'instruction header for source line number: 2',
             'instruction executor: Middle instruction',
             ])

    def test_last_instruction_fails(self):
        recording_media = RecordingMedia()
        instruction_executor = InstructionExecutorThatRecordsInstructionNameAndFailsFor(
            instruction_with_name('Last instruction'),
            recording_media.new_recorder_with_header('instruction executor'),
            PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.FAIL,
                                                    'fail message')
        )
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
                                                                  TestInstruction('First instruction')),
                                          new_instruction_element(Line(2, '2'),
                                                                TestInstruction('Last instruction'))
                                          ))
        self._standard_test(
            recording_media,
            phase_contents,
            instruction_executor,
            ExpectedResult(PartialResultStatus.FAIL,
                           Line(2, '2'),
                           new_expected_failure_message('fail message')),
            ['instruction header for source line number: 1',
             'instruction executor: First instruction',
             'instruction header for source line number: 2',
             'instruction executor: Last instruction',
             ])

    def test_comment_after_instruction_that_fails(self):
        recording_media = RecordingMedia()
        instruction_executor = InstructionExecutorThatRecordsInstructionNameAndFailsFor(
            any_instruction,
            recording_media.new_recorder_with_header('instruction executor'),
            PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.FAIL,
                                                    'fail message')
        )
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
                                                                  TestInstruction('First instruction')),
                                          new_comment_element(Line(50, '50')),
                                          ))
        self._standard_test(
            recording_media,
            phase_contents,
            instruction_executor,
            ExpectedResult(PartialResultStatus.FAIL,
                           Line(1, '1'),
                           new_expected_failure_message('fail message')),
            ['instruction header for source line number: 1',
             'instruction executor: First instruction',
             ])

    def _standard_test_with_successful_instruction_executor(self,
                                                            phase_contents: SectionContents,
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
                       phase_contents: SectionContents,
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
                 phase_contents: SectionContents,
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


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
