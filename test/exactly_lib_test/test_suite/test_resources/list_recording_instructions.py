from typing import List, Callable, Dict

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib_test.common.test_resources.instruction_documentation import instruction_documentation
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that


class StringRecorder:
    def __init__(self,
                 recording_media: List[str],
                 string_to_record: str):
        self.recording_media = recording_media
        self.string_to_record = string_to_record

    def __call__(self, *args, **kwargs):
        self.recording_media.append(self.string_to_record)


def mk_setup_phase_recording_instruction(main_action: Callable) -> SetupPhaseInstruction:
    return setup_phase_instruction_that(main_initial_action=main_action)


class InstructionParserForRecordingInstructions(InstructionParserWithoutSourceFileLocationInfo):
    def __init__(self,
                 recorder: List[str],
                 mk_instruction: Callable[[Callable], Instruction]):
        self.recorder = recorder
        self.mk_instruction = mk_instruction

    def parse_from_source(self, source: ParseSource) -> model.Instruction:
        str_to_record = source.remaining_part_of_current_line
        source.consume_current_line()
        return self.mk_instruction(StringRecorder(self.recorder, str_to_record))


def recording_instruction_setup(recorder: List[str]) -> SingleInstructionSetup:
    return SingleInstructionSetup(InstructionParserForRecordingInstructions(recorder,
                                                                            mk_setup_phase_recording_instruction),
                                  instruction_documentation('name-of-instruction'))


def instruction_setup_with_setup_instructions(name_of_registering_instruction: str,
                                              recording_media: List[str]) -> InstructionsSetup:
    return instruction_setup_with_single_phase_with_single_recording_instruction(
        name_of_registering_instruction,
        recording_media,
        mk_setup_phase_recording_instruction,
        mk_instruction_set_for_setup_phase)


def instruction_setup_with_single_phase_with_single_recording_instruction(
        name_of_registering_instruction: str,
        recording_media: List[str],
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
