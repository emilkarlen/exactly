from typing import List

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.test_case.result import sh
from exactly_lib_test.common.test_resources.instruction_documentation import instruction_documentation


class SetupPhaseInstructionThatRegistersString(SetupPhaseInstruction):
    def __init__(self,
                 recorder: List[str],
                 string_to_record: str):
        self.recorder = recorder
        self.string_to_record = string_to_record

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        self.recorder.append(self.string_to_record)
        return sh.new_sh_success()


class InstructionParserForRecordingInstructions(InstructionParserWithoutSourceFileLocationInfo):
    def __init__(self, recorder: List[str]):
        self.recorder = recorder

    def parse_from_source(self, source: ParseSource) -> model.Instruction:
        str_to_record = source.remaining_part_of_current_line
        source.consume_current_line()
        return SetupPhaseInstructionThatRegistersString(self.recorder, str_to_record)


def recording_instruction_setup(recorder: List[str]) -> SingleInstructionSetup:
    return SingleInstructionSetup(InstructionParserForRecordingInstructions(recorder),
                                  instruction_documentation('name-of-instruction'))


def instruction_name_extractor(line: str) -> str:
    return line.split(maxsplit=1)[0]


def instruction_setup(name_of_registering_instruction: str,
                      recorder: List[str]) -> InstructionsSetup:
    return InstructionsSetup({},
                             {name_of_registering_instruction: recording_instruction_setup(recorder)},
                             {}, {}, {})
