from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.result import sh
from exactly_lib.util.name_and_value import NameAndValue


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  actor_utils.InstructionDocumentation(instruction_name))


class Parser(InstructionParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource,
              ) -> model.Instruction:
        actor = actor_utils.parse(source)
        return Instruction(actor)


class Instruction(ConfigurationPhaseInstruction):
    def __init__(self, actor: NameAndValue[Actor]):
        self.actor = actor

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_actor(self.actor)
        return sh.new_sh_success()
