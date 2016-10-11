from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction, ConfigurationSectionEnvironment


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  actor_utils.InstructionDocumentation(instruction_name,
                                                                       _SINGLE_LINE_DESCRIPTION_UNFORMATTED,
                                                                       _DESCRIPTION))


_SINGLE_LINE_DESCRIPTION_UNFORMATTED = 'Sets an {actor} to use for each test case in the suite'
_DESCRIPTION = """\
The actor will treat the contents of the {act_phase} phase as source code
to be interpreted by the given program.

The {actor} may be overridden by configuration in test cases.

The {actor} is only used for the test cases in the current suite -
not in sub suites.


{EXECUTABLE} and {ARGUMENT} uses shell syntax.
"""


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> ConfigurationSectionInstruction:
        act_phase_handling = actor_utils.parse(source)
        return Instruction(ActPhaseSetup(act_phase_handling.source_and_executor_constructor))


class Instruction(ConfigurationSectionInstruction):
    def __init__(self,
                 act_phase_setup: ActPhaseSetup):
        self.act_phase_setup = act_phase_setup

    def execute(self,
                environment: ConfigurationSectionEnvironment):
        environment.act_phase_setup = self.act_phase_setup
