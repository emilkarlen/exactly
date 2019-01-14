import unittest

from typing import List, Sequence

from exactly_lib.definitions.formatting import SectionName
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document.model import InstructionInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedInstruction
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.section_document.source_location import FileSystemLocationInfo, FileLocationInfo
from exactly_lib.test_case.act_phase_handling import ActionToCheckExecutorParser, ActionToCheckExecutor
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.util.line_source import line_sequence_from_line, LineSequence
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_source_and_executors import \
    ActionToCheckExecutorThatJustReturnsSuccess
from exactly_lib_test.test_suite.case_instructions.test_resources import integration_test
from exactly_lib_test.test_suite.case_instructions.test_resources.integration_test import \
    PhaseConfig, \
    InstructionsSequencing
from exactly_lib_test.test_suite.test_resources.list_recording_instructions import Recording


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class ActPhaseConfig(PhaseConfig):
    def phase_name(self) -> SectionName:
        return phase_names.ACT

    def phase_contents_line_that_registers(self, marker_to_register: str) -> str:
        return marker_to_register

    def act_phase_parser(self) -> SectionElementParser:
        return ActPhaseParserThatConsumesCurrentLineAndGivesRecordingInstruction()

    def atc_executor_parser(self, recording_media: List[Recording]) -> ActionToCheckExecutorParser:
        return ActionToCheckExecutorParserThatRecordsInstructionData(recording_media)

    def instructions_setup(self,
                           register_instruction_name: str,
                           recording_media: List[Recording]) -> InstructionsSetup:
        return InstructionsSetup()


class Test(integration_test.TestBase):
    PHASE_CONFIG = ActPhaseConfig()

    def _phase_config(self) -> PhaseConfig:
        return self.PHASE_CONFIG

    def _expected_instruction_sequencing(self) -> InstructionsSequencing:
        return InstructionsSequencing.SUITE_BEFORE_CASE

    def test_instructions_in_containing_suite_SHOULD_be_be_included_first_in_each_case(self):
        self._phase_instructions_in_suite_containing_cases()

    def test_instructions_in_non_containing_suite_SHOULD_not_be_included_in_any_case(self):
        self._phase_instructions_in_suite_not_containing_cases()

    def test_WHEN_syntax_error_THEN_suite_reading_should_raise_exception(self):
        self._when_syntax_error_in_case_phase_contents_then_suite_reading_should_raise_exception()


class ActPhaseParserThatConsumesCurrentLineAndGivesRecordingInstruction(SectionElementParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> ParsedInstruction:
        current_line = source.current_line
        source.consume_current_line()
        instruction = ActPhaseInstructionThatRecords(fs_location_info.current_source_file,
                                                     current_line.text)
        return ParsedInstruction(line_sequence_from_line(current_line),
                                 InstructionInfo(instruction,
                                                 None))


class ActPhaseInstructionThatRecords(ActPhaseInstruction):
    def __init__(self,
                 file_location_info_to_record: FileLocationInfo,
                 marker_to_record: str):
        self.recording = Recording(file_location_info_to_record, marker_to_record)

    def source_code(self) -> LineSequence:
        raise NotImplementedError('should not be used')


class ActionToCheckExecutorParserThatRecordsInstructionData(ActionToCheckExecutorParser):
    def __init__(self, recording_media: List[Recording]):
        self.recording_media = recording_media

    def parse(self,
              act_phase_instructions: Sequence[ActPhaseInstruction]) -> ActionToCheckExecutor:
        for instruction in act_phase_instructions:
            assert isinstance(instruction, ActPhaseInstructionThatRecords)
            self.recording_media.append(instruction.recording)
        return ActionToCheckExecutorThatJustReturnsSuccess()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
