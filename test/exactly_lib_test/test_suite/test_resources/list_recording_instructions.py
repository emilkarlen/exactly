from typing import List, Callable, Dict

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParser
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo, FileLocationInfo
from exactly_lib.test_case.phases.setup.instruction import SetupPhaseInstruction
from exactly_lib_test.common.test_resources.instruction_documentation import instruction_documentation
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    SetupMainInitialAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class Recording:
    def __init__(self,
                 file_location_info: FileLocationInfo,
                 string: str,
                 ):
        self._string = string
        self._file_location_info = file_location_info

    @property
    def string(self) -> str:
        return self._string

    @property
    def file_location_info(self) -> FileLocationInfo:
        return self._file_location_info


def matches_recording(string: Assertion[str] = asrt.anything_goes(),
                      file_location_info: Assertion[FileLocationInfo] = asrt.anything_goes()
                      ) -> Assertion[Recording]:
    return asrt.and_([
        asrt.sub_component('string',
                           Recording.string.fget,
                           string
                           ),
        asrt.sub_component('file_location_info',
                           Recording.file_location_info.fget,
                           file_location_info,
                           ),
    ])


class StringRecorder:
    def __init__(self,
                 recording_media: List[Recording],
                 fs_location_info_to_record: FileSystemLocationInfo,
                 string_to_record: str):
        self.recording_media = recording_media
        self.fs_location_info_to_record = fs_location_info_to_record
        self.string_to_record = string_to_record

    def __call__(self, *args, **kwargs):
        self.recording_media.append(Recording(self.fs_location_info_to_record.current_source_file,
                                              self.string_to_record))


def mk_setup_phase_recording_instruction(main_action: SetupMainInitialAction) -> SetupPhaseInstruction:
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
