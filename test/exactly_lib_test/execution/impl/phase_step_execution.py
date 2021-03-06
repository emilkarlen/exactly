import unittest
from typing import Optional

from exactly_lib.execution.impl.phase_step_execution import execute_phase_prim
from exactly_lib.execution.impl.result import Failure
from exactly_lib.execution.impl.single_instruction_executor import ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum
from exactly_lib.execution.result import ExecutionFailureStatus
from exactly_lib.section_document.model import SectionContents
from exactly_lib.util.line_source import Line
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.execution.test_resources import failure_assertions as asrt_failure
from exactly_lib_test.execution.test_resources.phase_step_execution import RecordingMedia, \
    TestInstruction, ElementHeaderExecutorThatRecordsHeaderAndLineNumber, \
    InstructionExecutorThatRecordsInstructionNameAndReturnsSuccess, \
    InstructionExecutorThatRecordsInstructionNameAndFailsFor, TestException, \
    InstructionExecutorThatRecordsInstructionNameAndRaisesExceptionFor, any_instruction, instruction_with_name
from exactly_lib_test.section_document.test_resources.elements import new_comment_element, new_instruction_element
from exactly_lib_test.section_document.test_resources.source_location_assertions import \
    equals_single_line_source_location_path
from exactly_lib_test.test_case.result.test_resources import failure_details_assertions as asrt_failure_details
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_when_there_are_no_elements_no_executor_should_be_invoked_and_the_result_should_be_pass(self):
        phase_contents = SectionContents(())
        self._standard_test_with_successful_instruction_executor(
            phase_contents,
            asrt_failure.is_not_present(),
            [])

    def test_when_there_are_only_comment_elements_than_the_result_should_be_pass(self):
        phase_contents = SectionContents((new_comment_element(Line(1, '1')),
                                          new_comment_element(Line(2, '2'))))
        self._standard_test_with_successful_instruction_executor(
            phase_contents,
            asrt_failure.is_not_present(),
            ['comment header for source line number: 1',
             'comment header for source line number: 2'])

    def test_successful_execution_of_single_instruction(self):
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
                                                                  TestInstruction('The instruction')),
                                          ))
        self._standard_test_with_successful_instruction_executor(
            phase_contents,
            asrt_failure.is_not_present(),
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
            asrt_failure.is_not_present(),
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
            PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.FAIL,
                asrt_text_doc.new_single_string_text_for_test('fail message')
            )
        )
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
                                                                  TestInstruction('The instruction')),
                                          ))
        self._standard_test(
            recording_media,
            phase_contents,
            instruction_executor,
            asrt_failure.is_present_with(ExecutionFailureStatus.FAIL,
                                         equals_single_line_source_location_path(Line(1, '1')),
                                         asrt_failure_details.is_failure_message_of('fail message')),
            ['instruction header for source line number: 1',
             'instruction executor: The instruction'])

    def test_single_failing_instruction_executor__status_hard_error(self):
        recording_media = RecordingMedia()
        instruction_executor = InstructionExecutorThatRecordsInstructionNameAndFailsFor(
            any_instruction,
            recording_media.new_recorder_with_header('instruction executor'),
            PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.HARD_ERROR,
                asrt_text_doc.new_single_string_text_for_test('hard error message')
            )
        )
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
                                                                  TestInstruction('The instruction')),
                                          ))
        self._standard_test(
            recording_media,
            phase_contents,
            instruction_executor,
            asrt_failure.is_present_with(ExecutionFailureStatus.HARD_ERROR,
                                         equals_single_line_source_location_path(Line(1, '1')),
                                         asrt_failure_details.is_failure_message_of('hard error message')),
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
            asrt_failure.is_present_with(ExecutionFailureStatus.INTERNAL_ERROR,
                                         equals_single_line_source_location_path(Line(1, '1')),
                                         asrt_failure_details.is_exception_of_type(TestException)),
            ['instruction header for source line number: 1',
             'instruction executor: The instruction'])

    def test_first_instruction_fails(self):
        recording_media = RecordingMedia()
        instruction_executor = InstructionExecutorThatRecordsInstructionNameAndFailsFor(
            instruction_with_name('First instruction'),
            recording_media.new_recorder_with_header('instruction executor'),
            PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.FAIL,
                asrt_text_doc.new_single_string_text_for_test('fail message')
            )
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
            asrt_failure.is_present_with(ExecutionFailureStatus.FAIL,
                                         equals_single_line_source_location_path(Line(1, '1')),
                                         asrt_failure_details.is_failure_message_of('fail message')),
            ['instruction header for source line number: 1',
             'instruction executor: First instruction'])

    def test_middle_instruction_fails(self):
        recording_media = RecordingMedia()
        instruction_executor = InstructionExecutorThatRecordsInstructionNameAndFailsFor(
            instruction_with_name('Middle instruction'),
            recording_media.new_recorder_with_header('instruction executor'),
            PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.FAIL,
                asrt_text_doc.new_single_string_text_for_test('fail message')
            )
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
            asrt_failure.is_present_with(ExecutionFailureStatus.FAIL,
                                         equals_single_line_source_location_path(Line(2, '2')),
                                         asrt_failure_details.is_failure_message_of('fail message')),
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
            PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.FAIL,
                asrt_text_doc.new_single_string_text_for_test('fail message')
            )
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
            asrt_failure.is_present_with(ExecutionFailureStatus.FAIL,
                                         equals_single_line_source_location_path(Line(2, '2')),
                                         asrt_failure_details.is_failure_message_of('fail message')),
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
            PartialInstructionControlledFailureInfo(
                PartialControlledFailureEnum.FAIL,
                asrt_text_doc.new_single_string_text_for_test('fail message')
            )
        )
        phase_contents = SectionContents((new_instruction_element(Line(1, '1'),
                                                                  TestInstruction('First instruction')),
                                          new_comment_element(Line(50, '50')),
                                          ))
        self._standard_test(
            recording_media,
            phase_contents,
            instruction_executor,
            asrt_failure.is_present_with(ExecutionFailureStatus.FAIL,
                                         equals_single_line_source_location_path(Line(1, '1')),
                                         asrt_failure_details.is_failure_message_of('fail message')),
            ['instruction header for source line number: 1',
             'instruction executor: First instruction',
             ])

    def _standard_test_with_successful_instruction_executor(self,
                                                            phase_contents: SectionContents,
                                                            expected_result: Assertion[Optional[Failure]],
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
                       expected_result: Assertion[Optional[Failure]],
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
                expected_result: Assertion[Optional[Failure]],
                actual_result: Failure,
                expected_recordings: list,
                actual_recording_media: RecordingMedia):
        expected_result.apply_with_message(self,
                                           actual_result,
                                           'failure')
        self.assertEqual(expected_recordings,
                         actual_recording_media.output,
                         'Recorded executions')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
