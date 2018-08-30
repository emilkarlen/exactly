from typing import List, Callable, Dict

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParser
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib_test.common.test_resources.instruction_documentation import instruction_documentation
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Recording:
    def __init__(self, string: str):
        self._string = string

    @property
    def string(self) -> str:
        return self._string


def matches_recording(string: str) -> asrt.ValueAssertion[Recording]:
    return asrt.sub_component('string',
                              Recording.string.fget,
                              asrt.equals(string))


class StringRecorder:
    def __init__(self,
                 recording_media: List[Recording],
                 fs_location_info_to_record: FileSystemLocationInfo,
                 string_to_record: str):
        self.recording_media = recording_media
        self.fs_location_info_to_record = fs_location_info_to_record
        self.string_to_record = string_to_record

    def __call__(self, *args, **kwargs):
        self.recording_media.append(Recording(self.string_to_record))


def mk_setup_phase_recording_instruction(main_action: Callable) -> SetupPhaseInstruction:
    return setup_phase_instruction_that(main_initial_action=main_action)


class InstructionParserForRecordingInstructions(InstructionParser):
    def __init__(self,
                 recorder: List[Recording],
                 mk_instruction: Callable[[Callable], Instruction]):
        self.recorder = recorder
        self.mk_instruction = mk_instruction

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> model.Instruction:
        str_to_record = source.remaining_part_of_current_line
        source.consume_current_line()
        return self.mk_instruction(StringRecorder(self.recorder, fs_location_info, str_to_record))


def recording_instruction_setup(recorder: List[Recording]) -> SingleInstructionSetup:
    return SingleInstructionSetup(InstructionParserForRecordingInstructions(recorder,
                                                                            mk_setup_phase_recording_instruction),
                                  instruction_documentation('name-of-instruction'))


def instruction_setup_with_setup_instructions(name_of_registering_instruction: str,
                                              recording_media: List[Recording]) -> InstructionsSetup:
    return instruction_setup_with_single_phase_with_single_recording_instruction(
        name_of_registering_instruction,
        recording_media,
        mk_setup_phase_recording_instruction,
        mk_instruction_set_for_setup_phase)


def instruction_setup_with_single_phase_with_single_recording_instruction(
        name_of_registering_instruction: str,
        recording_media: List[Recording],
        mk_instruction_with_main_action: Callable[[Callable], Instruction],
        mk_instruction_set_for_single_phase: Callable[[Dict[str, SingleInstructionSetup]], InstructionsSetup],
) -> InstructionsSetup:
    instruction_setup = SingleInstructionSetup(
        InstructionParserForRecordingInstructions(recording_media,
                                                  mk_instruction_with_main_action),
        instruction_documentation('name-of-instruction'))

    phase_instructions = {
        name_of_registering_instruction: instruction_setup
    }

    return mk_instruction_set_for_single_phase(phase_instructions)


def mk_instruction_set_for_setup_phase(instructions: Dict[str, SingleInstructionSetup]) -> InstructionsSetup:
    return InstructionsSetup(setup_instruction_set=instructions)
