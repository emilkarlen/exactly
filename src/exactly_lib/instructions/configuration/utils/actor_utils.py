import shlex

from exactly_lib.act_phase_setups import shell_command
from exactly_lib.act_phase_setups.source_interpreter import shell_command_interpreter_setup as shell_cmd
from exactly_lib.act_phase_setups.source_interpreter.interpreter_setup import new_for_script_language_handling
from exactly_lib.act_phase_setups.source_interpreter.source_file_management import SourceInterpreterSetup
from exactly_lib.act_phase_setups.source_interpreter.source_file_management import StandardSourceFileManager
from exactly_lib.common.instruction_documentation import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.phase_names import ACT_PHASE_NAME
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

SHELL_COMMAND_OPTION_NAME = a.OptionName(long_name='shell')
SHELL_COMMAND_OPTION = long_option_syntax(SHELL_COMMAND_OPTION_NAME.long)

SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD = '$'

INTERPRETER_OPTION_NAME = a.OptionName(long_name='interpreter')
INTERPRETER_OPTION = long_option_syntax(INTERPRETER_OPTION_NAME.long)


class InstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str,
                 single_line_description_unformatted: str,
                 main_description_rest_unformatted: str = None):
        self.executable = a.Named('EXECUTABLE')
        self.argument = a.Named('ARGUMENT')
        self.command = a.Constant('COMMAND')
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
        shell_arg = a.Single(a.Multiplicity.MANDATORY, a.Option(SHELL_COMMAND_OPTION_NAME))
        interpreter_arg = a.Single(a.Multiplicity.OPTIONAL, a.Option(INTERPRETER_OPTION_NAME))
        executable_arg = a.Single(a.Multiplicity.MANDATORY, self.executable)
        optional_arguments_arg = a.Single(a.Multiplicity.ZERO_OR_MORE, self.argument)
        shell_interpreter_argument = a.Single(a.Multiplicity.MANDATORY,
                                              a.Constant(SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD))
        command_argument = a.Single(a.Multiplicity.MANDATORY, self.command)
        return [
            InvokationVariant(self._cl_syntax_for_args([shell_arg]),
                              self._description_of_shell()),
            InvokationVariant(self._cl_syntax_for_args([interpreter_arg,
                                                        executable_arg,
                                                        optional_arguments_arg]),
                              self._description_of_interpreter()),
            InvokationVariant(self._cl_syntax_for_args([interpreter_arg,
                                                        shell_interpreter_argument,
                                                        command_argument]),
                              self._description_of_shell_command_interpreter()),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(self.executable.name,
                                     self._paragraphs(_DESCRIPTION_OF_EXECUTABLE)),
            SyntaxElementDescription(self.argument.name,
                                     self._paragraphs(_DESCRIPTION_OF_ARGUMENTS)),
            SyntaxElementDescription(self.command.name,
                                     self._paragraphs(_DESCRIPTION_OF_COMMAND))
        ]

    def main_description_rest(self) -> list:
        if self.main_description_rest_unformatted:
            return self._paragraphs(self.main_description_rest_unformatted)
        else:
            return []

    def see_also(self) -> list:
        from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        from exactly_lib.help.actors.names_and_cross_references import all_actor_cross_refs
        return [ACTOR_CONCEPT.cross_reference_target()] + all_actor_cross_refs()

    def _description_of_interpreter(self) -> list:
        from exactly_lib.help.actors.names_and_cross_references import INTERPRETER_ACTOR
        return self._paragraphs(_DESCRIPTION_OF_INTERPRETER, {
            'interpreter_actor': formatting.entity(INTERPRETER_ACTOR.singular_name)
        })

    def _description_of_shell_command_interpreter(self) -> list:
        from exactly_lib.help.actors.names_and_cross_references import INTERPRETER_ACTOR
        return self._paragraphs(_DESCRIPTION_OF_SHELL_COMMAND_INTERPRETER, {
            'interpreter_actor': formatting.entity(INTERPRETER_ACTOR.singular_name)
        })

    def _description_of_shell(self) -> list:
        from exactly_lib.help.actors.names_and_cross_references import SHELL_COMMAND_LINE_ACTOR
        return self._paragraphs(_DESCRIPTION_OF_SHELL, {
            'shell_command_actor': formatting.entity(SHELL_COMMAND_LINE_ACTOR.singular_name)
        })


def parse(source: SingleInstructionParserSource) -> ActPhaseHandling:
    """
    :raises SingleInstructionInvalidArgumentException In case of invalid syntax
    """
    arg = source.instruction_argument.strip()
    if arg == '':
        raise SingleInstructionInvalidArgumentException('An actor must be given')
    if arg == SHELL_COMMAND_OPTION:
        return shell_command.act_phase_setup()
    args = arg.split(maxsplit=1)
    if args:
        if args[0] == SHELL_COMMAND_OPTION and len(args) > 1:
            raise SingleInstructionInvalidArgumentException('Superfluous arguments')
    if len(args) > 0 and args[0] == INTERPRETER_OPTION:
        if len(args) == 1:
            raise SingleInstructionInvalidArgumentException('Missing interpreter')
        return _parse_interpreter(args[1])
    else:
        return _parse_interpreter(arg)


def _parse_interpreter(arg: str) -> ActPhaseHandling:
    args = arg.split(maxsplit=1)
    if not args:
        raise SingleInstructionInvalidArgumentException('Missing interpreter')
    if args[0] == SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD:
        if len(args) == 1:
            raise SingleInstructionInvalidArgumentException('Missing shell command for interpreter')
        else:
            return shell_cmd.handling_for_interpreter_command(args[1])
    try:
        command_and_arguments = shlex.split(arg)
    except:
        raise SingleInstructionInvalidArgumentException('Invalid quoting: ' + arg)
    if not command_and_arguments:
        raise SingleInstructionInvalidArgumentException('Missing interpreter')

    act_phase_setup = new_for_script_language_handling(
        SourceInterpreterSetup(StandardSourceFileManager(
            'src',
            command_and_arguments[0],
            command_and_arguments[1:])))
    return act_phase_setup


_DESCRIPTION_OF_INTERPRETER = """\
Sets the {interpreter_actor} {actor}, with an executable program as interpreter.
"""

_DESCRIPTION_OF_SHELL_COMMAND_INTERPRETER = """\
Sets the {interpreter_actor} {actor}, with a shell command as interpreter.
"""

_DESCRIPTION_OF_SHELL = """\
Sets the {shell_command_actor} {actor}.
"""

_DESCRIPTION_OF_EXECUTABLE = """\
The path of an existing executable file.


Uses shell syntax.
"""

_DESCRIPTION_OF_COMMAND = """\
A shell command line.


Uses the syntax of the operating system's shell.
(Which shell this is depends on the operating system).
"""

_DESCRIPTION_OF_ARGUMENTS = """\
Arguments given to {EXECUTABLE}.


Uses shell syntax.
"""
