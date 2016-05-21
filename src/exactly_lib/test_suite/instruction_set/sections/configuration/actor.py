import shlex

import exactly_lib.act_phase_setups.script_interpretation.script_language_management
from exactly_lib.act_phase_setups.script_interpretation import generic_script_language
from exactly_lib.act_phase_setups.script_interpretation.script_language_management import ScriptLanguageSetup
from exactly_lib.act_phase_setups.script_interpretation.script_language_setup import new_for_script_language_setup
from exactly_lib.common.instruction_documentation import InvokationVariant, SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.help.concepts.plain_concepts.actor import ACTOR_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.phase_names import ACT_PHASE_NAME
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction, ConfigurationSectionEnvironment
from exactly_lib.util.cli_syntax.elements import argument as a


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(Parser(),
                                  TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        self.executable = a.Named('EXECUTABLE')
        self.argument = a.Named('ARGUMENT')
        super().__init__(name, {
            'EXECUTABLE': self.executable.name,
            'ARGUMENT': self.argument.name,
            'actor': formatting.concept(ACTOR_CONCEPT.name().singular),
            'act_phase': ACT_PHASE_NAME.emphasis,
        })

    def single_line_description(self) -> str:
        return self._format('Sets an {actor} to use for each test case in the suite')

    def invokation_variants(self) -> list:
        executable_arg = a.Single(a.Multiplicity.MANDATORY,
                                  self.executable)
        optional_arguments_arg = a.Single(a.Multiplicity.ZERO_OR_MORE,
                                          self.argument)
        return [
            InvokationVariant(self._cl_syntax_for_args([executable_arg,
                                                        optional_arguments_arg])),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(self.executable.name,
                                     self._paragraphs('The path of an existing executable file.'))
        ]

    def main_description_rest(self) -> list:
        return self._paragraphs(_DESCRIPTION)

    def see_also(self) -> list:
        return [
            ACTOR_CONCEPT.cross_reference_target(),
        ]


_DESCRIPTION = """\
The actor will treat the contents of the {act_phase} phase as source code
to be interpreted by the given program.


The {actor} is only used for the test cases in the current suite -
not in sub suites.


{EXECUTABLE} and {ARGUMENT} uses shell syntax.
"""


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> ConfigurationSectionInstruction:
        arg = source.instruction_argument.strip()
        if arg == '':
            raise SingleInstructionInvalidArgumentException('A preprocessor program must be given.')
        try:
            command_and_arguments = shlex.split(arg)
        except:
            raise SingleInstructionInvalidArgumentException('Invalid quoting: ' + arg)
        act_phase_setup = new_for_script_language_setup(
            ScriptLanguageSetup(
                exactly_lib.act_phase_setups.script_interpretation.script_language_management.StandardScriptFileManager(
                    'src',
                    command_and_arguments[0],
                                                                   command_and_arguments[1:]),
                generic_script_language.StandardScriptLanguage()))
        return Instruction(act_phase_setup)


class Instruction(ConfigurationSectionInstruction):
    def __init__(self,
                 act_phase_setup: ActPhaseSetup):
        self.act_phase_setup = act_phase_setup

    def execute(self,
                environment: ConfigurationSectionEnvironment):
        """
        Updates the environment.
        """
        environment.act_phase_setup = self.act_phase_setup
