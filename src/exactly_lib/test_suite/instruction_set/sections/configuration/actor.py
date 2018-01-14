from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.section_document.element_parsers.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction, ConfigurationSectionEnvironment


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  actor_utils.InstructionDocumentation(instruction_name,
                                                                       _SINGLE_LINE_DESCRIPTION_UNFORMATTED,
                                                                       _DESCRIPTION))


_SINGLE_LINE_DESCRIPTION_UNFORMATTED = 'Sets an {actor} to use for each test case in the suite'
_DESCRIPTION = """\
The {actor} may be overridden by configuration in test cases.

The {actor} is only used for the test cases in the current suite -
not in sub suites.
"""


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> ConfigurationSectionInstruction:
        act_phase_handling = actor_utils.parse(rest_of_line)
        return Instruction(ActPhaseSetup(act_phase_handling.source_and_executor_constructor))


class Instruction(ConfigurationSectionInstruction):
    def __init__(self,
                 act_phase_setup: ActPhaseSetup):
        self.act_phase_setup = act_phase_setup

    def execute(self,
                environment: ConfigurationSectionEnvironment):
        environment.act_phase_setup = self.act_phase_setup
