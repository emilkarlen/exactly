from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionEnvironment, ConfigurationSectionInstruction
from exactly_lib_test.processing.processing_utils import PreprocessorThat
from exactly_lib_test.processing.test_resources.act_phase import command_line_actor_setup

INSTRUCTION_NAME__ACTOR = 'actor'


def configuration_section_environment() -> ConfigurationSectionEnvironment:
    def f():
        pass

    return ConfigurationSectionEnvironment(PreprocessorThat(f),
                                           command_line_actor_setup())


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  actor_utils.InstructionDocumentation(instruction_name))


class Parser(InstructionParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource,
              ) -> ConfigurationSectionInstruction:
        actor = actor_utils.parse(source)
        return Instruction(ActPhaseSetup.of_nav(actor))


class Instruction(ConfigurationSectionInstruction):
    def __init__(self, act_phase_setup: ActPhaseSetup):
        self.act_phase_setup = act_phase_setup

    def execute(self, environment: ConfigurationSectionEnvironment):
        environment.act_phase_setup = self.act_phase_setup
