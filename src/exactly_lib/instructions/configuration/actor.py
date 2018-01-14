from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import sh


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
        act_phase_handling = actor_utils.parse(rest_of_line)
        return Instruction(act_phase_handling)


class Instruction(ConfigurationPhaseInstruction):
    def __init__(self,
                 act_phase_handling: ActPhaseHandling):
        self.act_phase_handling = act_phase_handling

    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_act_phase_handling(self.act_phase_handling)
        return sh.new_sh_success()
