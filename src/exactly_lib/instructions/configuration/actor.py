from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.execution.act_phase import ActPhaseHandling
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import sh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  actor_utils.InstructionDocumentation(instruction_name,
                                                                       _SINGLE_LINE_DESCRIPTION_UNFORMATTED,
                                                                       _DESCRIPTION))


_SINGLE_LINE_DESCRIPTION_UNFORMATTED = 'Sets the {actor} that will execute the {act_phase} phase'
_DESCRIPTION = """\
The actor will treat the contents of the {act_phase} phase as source code
to be interpreted by the given program.


{EXECUTABLE} and {ARGUMENT} uses shell syntax.
"""


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> ConfigurationPhaseInstruction:
        act_phase_setup = actor_utils.parse(source)
        return Instruction(act_phase_setup)


class Instruction(ConfigurationPhaseInstruction):
    def __init__(self,
                 act_phase_handling: ActPhaseHandling):
        self.act_phase_handling = act_phase_handling

    def main(self,
             global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_act_phase_handling(self.act_phase_handling)
        return sh.new_sh_success()
