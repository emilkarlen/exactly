import shlex

from exactly_lib.act_phase_setups import command_line
from exactly_lib.act_phase_setups import file_interpreter
from exactly_lib.act_phase_setups import interpreter as source_interpreter
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help.actors.actor import command_line as command_line_actor_help
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.phase_names import ACT_PHASE_NAME
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_parsing import matches
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.process_execution.os_process_execution import Command

COMMAND_LINE_ACTOR_OPTION_NAME = a.OptionName(long_name='command')
COMMAND_LINE_ACTOR_OPTION = long_option_syntax(COMMAND_LINE_ACTOR_OPTION_NAME.long)

SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD = '$'

SOURCE_INTERPRETER_OPTION_NAME = a.OptionName(long_name='source')
SOURCE_INTERPRETER_OPTION = long_option_syntax(SOURCE_INTERPRETER_OPTION_NAME.long)

FILE_INTERPRETER_OPTION_NAME = a.OptionName(long_name='file')
FILE_INTERPRETER_OPTION = long_option_syntax(FILE_INTERPRETER_OPTION_NAME.long)


class InstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str,
                 single_line_description_unformatted: str,
                 main_description_rest_unformatted: str = None):
        self.command_line_syntax = command_line_actor_help.ActPhaseDocumentationSyntax()
        self.single_line_description_unformatted = single_line_description_unformatted
        self.main_description_rest_unformatted = main_description_rest_unformatted
        from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        super().__init__(name, {
            'EXECUTABLE': self.command_line_syntax.executable.name,
            'ARGUMENT': self.command_line_syntax.argument.name,
            'actor': formatting.concept(ACTOR_CONCEPT.name().singular),
            'act_phase': ACT_PHASE_NAME.emphasis,
        })

    def single_line_description(self) -> str:
        return self._format(self.single_line_description_unformatted)

    def invokation_variants(self) -> list:
        command_line_actor_arg = a.Single(a.Multiplicity.MANDATORY, a.Option(COMMAND_LINE_ACTOR_OPTION_NAME))
        source_interpreter_arg = a.Single(a.Multiplicity.OPTIONAL, a.Option(SOURCE_INTERPRETER_OPTION_NAME))
        executable_arg = a.Single(a.Multiplicity.MANDATORY, self.command_line_syntax.executable)
        optional_arguments_arg = a.Single(a.Multiplicity.ZERO_OR_MORE, self.command_line_syntax.argument)
        shell_interpreter_argument = a.Single(a.Multiplicity.MANDATORY,
                                              a.Constant(SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD))
        command_argument = a.Single(a.Multiplicity.MANDATORY, self.command_line_syntax.command)
        return [
            InvokationVariant(self._cl_syntax_for_args([command_line_actor_arg]),
                              self._description_of_command_line()),
            InvokationVariant(self._cl_syntax_for_args([source_interpreter_arg,
                                                        executable_arg,
                                                        optional_arguments_arg]),
                              self._description_of_interpreter()),
            InvokationVariant(self._cl_syntax_for_args([source_interpreter_arg,
                                                        shell_interpreter_argument,
                                                        command_argument]),
                              self._description_of_shell_command_interpreter()),
        ]

    def syntax_element_descriptions(self) -> list:
        return self.command_line_syntax.syntax_element_descriptions()

    def main_description_rest(self) -> list:
        if self.main_description_rest_unformatted:
            return self._paragraphs(self.main_description_rest_unformatted)
        else:
            return []

    def _see_also_cross_refs(self) -> list:
        from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        from exactly_lib.help.actors.names_and_cross_references import all_actor_cross_refs
        return ([ACTOR_CONCEPT.cross_reference_target()] +
                all_actor_cross_refs() +
                command_line_actor_help.see_also_targets())

    def _description_of_interpreter(self) -> list:
        from exactly_lib.help.actors.names_and_cross_references import SOURCE_INTERPRETER_ACTOR
        return self._paragraphs(_DESCRIPTION_OF_SOURCE_INTERPRETER, {
            'interpreter_actor': formatting.entity(SOURCE_INTERPRETER_ACTOR.singular_name)
        })

    def _description_of_shell_command_interpreter(self) -> list:
        from exactly_lib.help.actors.names_and_cross_references import SOURCE_INTERPRETER_ACTOR
        return self._paragraphs(_DESCRIPTION_OF_SHELL_COMMAND_SOURCE_INTERPRETER, {
            'interpreter_actor': formatting.entity(SOURCE_INTERPRETER_ACTOR.singular_name)
        })

    def _description_of_command_line(self) -> list:
        from exactly_lib.help.actors.names_and_cross_references import COMMAND_LINE_ACTOR
        return self._paragraphs(_DESCRIPTION_OF_SHELL, {
            'command_line_actor': formatting.entity(COMMAND_LINE_ACTOR.singular_name)
        })


def parse(source: SingleInstructionParserSource) -> ActPhaseHandling:
    """
    :raises SingleInstructionInvalidArgumentException In case of invalid syntax
    """
    arg = source.instruction_argument.strip()
    if not arg:
        raise SingleInstructionInvalidArgumentException('An actor must be given')
    try:
        args = arg.split(maxsplit=1)
    except Exception as ex:
        raise SingleInstructionInvalidArgumentException(str(ex))
    if matches(COMMAND_LINE_ACTOR_OPTION_NAME, args[0]):
        if len(args) > 1:
            raise SingleInstructionInvalidArgumentException('Superfluous arguments to ' + args[0])
        return command_line.act_phase_handling()
    if len(args) == 1:
        raise SingleInstructionInvalidArgumentException('Missing file argument for ' + args[0])
    if matches(SOURCE_INTERPRETER_OPTION_NAME, args[0]):
        return _parse_source_interpreter(args[1])
    if matches(FILE_INTERPRETER_OPTION_NAME, args[0]):
        return _parse_file_interpreter(args[1])
    raise SingleInstructionInvalidArgumentException('Invalid option: "{}"'.format(args[0]))


def _parse_source_interpreter(arg: str) -> ActPhaseHandling:
    return source_interpreter.act_phase_handling(_parse_source_interpreter_command(arg))


def _parse_file_interpreter(arg: str) -> ActPhaseHandling:
    return file_interpreter.act_phase_handling(_parse_file_interpreter_command(arg))


def _parse_source_interpreter_command(arg: str) -> Command:
    args = arg.split(maxsplit=1)
    if not args:
        raise SingleInstructionInvalidArgumentException('Missing source interpreter')
    if args[0] == SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD:
        if len(args) == 1:
            raise SingleInstructionInvalidArgumentException('Missing shell command for source interpreter')
        else:
            return Command(args[1], shell=True)
    command_and_arguments = shlex_split(arg)
    if not command_and_arguments:
        raise SingleInstructionInvalidArgumentException('Missing source interpreter')
    return Command(command_and_arguments, shell=False)


def _parse_file_interpreter_command(arg: str) -> Command:
    command_and_arguments = shlex_split(arg)
    if not command_and_arguments:
        raise SingleInstructionInvalidArgumentException('Missing file interpreter')
    return Command(command_and_arguments, shell=False)


def shlex_split(s: str) -> list:
    try:
        return shlex.split(s)
    except:
        raise SingleInstructionInvalidArgumentException('Invalid quoting: ' + s)


_DESCRIPTION_OF_SOURCE_INTERPRETER = """\
Specifies that the {interpreter_actor} {actor} should be used, with an executable program as interpreter.
"""

_DESCRIPTION_OF_SHELL_COMMAND_SOURCE_INTERPRETER = """\
Specifies that the {interpreter_actor} {actor} should be used, with a shell command as interpreter.
"""

_DESCRIPTION_OF_SHELL = """\
Specifies that the {command_line_actor} {actor} should be used.
"""
