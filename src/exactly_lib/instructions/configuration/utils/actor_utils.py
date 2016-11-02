import shlex

from exactly_lib.act_phase_setups import shell_command
from exactly_lib.act_phase_setups.script_interpretation.script_language_management import ScriptLanguageSetup
from exactly_lib.act_phase_setups.script_interpretation.script_language_management import StandardScriptFileManager
from exactly_lib.act_phase_setups.script_interpretation.script_language_setup import new_for_script_language_handling
from exactly_lib.common.instruction_documentation import InvokationVariant, SyntaxElementDescription
from exactly_lib.execution.act_phase import ActPhaseHandling
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.phase_names import ACT_PHASE_NAME
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.util.cli_syntax.elements import argument as a

SHELL_COMMAND_ACTOR_KEYWORD = 'shell'

INTERPRETER_ACTOR_KEYWORD = 'interpreter'


class InstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str,
                 single_line_description_unformatted: str,
                 main_description_rest_unformatted: str):
        self.executable = a.Named('EXECUTABLE')
        self.argument = a.Named('ARGUMENT')
        self.single_line_description_unformatted = single_line_description_unformatted
        self.main_description_rest_unformatted = main_description_rest_unformatted
        from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        super().__init__(name, {
            'EXECUTABLE': self.executable.name,
            'ARGUMENT': self.argument.name,
            'actor': formatting.concept(ACTOR_CONCEPT.name().singular),
            'act_phase': ACT_PHASE_NAME.emphasis,
        })

    def single_line_description(self) -> str:
        return self._format(self.single_line_description_unformatted)

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
        return self._paragraphs(self.main_description_rest_unformatted)

    def see_also(self) -> list:
        from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        return [
            ACTOR_CONCEPT.cross_reference_target(),
        ]


def parse(source: SingleInstructionParserSource) -> ActPhaseHandling:
    """
    :raises SingleInstructionInvalidArgumentException In case of invalid syntax
    """
    arg = source.instruction_argument.strip()
    if arg == '':
        raise SingleInstructionInvalidArgumentException('An actor must be given.')
    if arg == SHELL_COMMAND_ACTOR_KEYWORD:
        return shell_command.act_phase_setup()
    args = arg.split(maxsplit=1)
    if args:
        if args[0] == SHELL_COMMAND_ACTOR_KEYWORD and len(args) > 1:
            raise SingleInstructionInvalidArgumentException('Superfluous argument to ' + SHELL_COMMAND_ACTOR_KEYWORD)
    try:
        command_and_arguments = shlex.split(arg)
    except:
        raise SingleInstructionInvalidArgumentException('Invalid quoting: ' + arg)
    if len(command_and_arguments) > 0 and command_and_arguments[0] == INTERPRETER_ACTOR_KEYWORD:
        del command_and_arguments[0]
    if not command_and_arguments:
        raise SingleInstructionInvalidArgumentException('Missing interpreter')

    act_phase_setup = new_for_script_language_handling(
        ScriptLanguageSetup(StandardScriptFileManager(
            'src',
            command_and_arguments[0],
            command_and_arguments[1:])))
    return act_phase_setup
