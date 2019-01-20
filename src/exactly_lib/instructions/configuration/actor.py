from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.result import sh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  actor_utils.InstructionDocumentation(instruction_name,
                                                                       _SINGLE_LINE_DESCRIPTION_UNFORMATTED,
                                                                       _MAIN_DESCRIPTION_REST_UNFORMATTED))


_SINGLE_LINE_DESCRIPTION_UNFORMATTED = 'Specifies the {actor} that will execute the {act_phase} phase'

_MAIN_DESCRIPTION_REST_UNFORMATTED = """\
The {actor} specified by this instruction has precedence over all other ways
to specify the actor.
"""


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> ConfigurationPhaseInstruction:
        actor = actor_utils.parse(rest_of_line)
        return Instruction(actor)


class Instruction(ConfigurationPhaseInstruction):
    def __init__(self, actor: Actor):
        self.actor = actor

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_actor(self.actor)
        return sh.new_sh_success()
