import shlex
from typing import List

from exactly_lib.actors import command_line, file_interpreter
from exactly_lib.actors import source_interpreter as source_interpreter
from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args
from exactly_lib.definitions import formatting, instruction_arguments
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.definitions.entity import concepts, actors
from exactly_lib.definitions.entity.actors import FILE_INTERPRETER_ACTOR
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.help.entities.actors.objects import command_line as command_line_actor_help
from exactly_lib.instructions.configuration.utils.single_arg_utils import MANDATORY_EQ_ARG
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case_utils.parse.shell_syntax import SHELL_KEYWORD
from exactly_lib.type_system.logic.program.process_execution import commands
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_parsing import matches
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.textformat.structure.core import ParagraphItem

COMMAND_LINE_ACTOR_OPTION_NAME = a.OptionName(long_name='command')
COMMAND_LINE_ACTOR_OPTION = long_option_syntax(COMMAND_LINE_ACTOR_OPTION_NAME.long)

SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD = SHELL_KEYWORD

SOURCE_INTERPRETER_OPTION_NAME = a.OptionName(long_name='source')
SOURCE_INTERPRETER_OPTION = long_option_syntax(SOURCE_INTERPRETER_OPTION_NAME.long)

FILE_INTERPRETER_OPTION_NAME = a.OptionName(long_name='file')
FILE_INTERPRETER_OPTION = long_option_syntax(FILE_INTERPRETER_OPTION_NAME.long)


class InstructionDocumentation(InstructionDocumentationWithTextParserBase):
    def __init__(self, name: str,
                 single_line_description_un_formatted: str,
                 main_description_rest_un_formatted: str = None):
        self.command_line_syntax = command_line_actor_help.ActPhaseDocumentationSyntax()
        self.single_line_description_un_formatted = single_line_description_un_formatted
        self.main_description_rest_un_formatted = main_description_rest_un_formatted
        super().__init__(name, {
            'EXECUTABLE': self.command_line_syntax.executable.name,
            'ARGUMENT': self.command_line_syntax.argument.name,
            'actor': formatting.concept_(concepts.ACTOR_CONCEPT_INFO),
            'act_phase': phase_names.ACT.emphasis,
            'command_line_actor': formatting.entity_(actors.COMMAND_LINE_ACTOR)
        })

    def single_line_description(self) -> str:
        return self._tp.format(self.single_line_description_un_formatted)

    def invokation_variants(self) -> list:
        from exactly_lib.definitions.entity.actors import SOURCE_INTERPRETER_ACTOR
        source_interpreter_arg = a.Single(a.Multiplicity.MANDATORY, a.Option(SOURCE_INTERPRETER_OPTION_NAME))
        file_interpreter_arg = a.Single(a.Multiplicity.MANDATORY, a.Option(FILE_INTERPRETER_OPTION_NAME))
        return (self._command_line_invokation_variants() +
                self._interpreter_actor_invokation_variants(FILE_INTERPRETER_ACTOR,
                                                            file_interpreter_arg) +
                self._interpreter_actor_invokation_variants(SOURCE_INTERPRETER_ACTOR,
                                                            source_interpreter_arg))

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return self.command_line_syntax.syntax_element_descriptions_for_executable_as_system_command()

    def main_description_rest(self) -> List[ParagraphItem]:
        if self.main_description_rest_un_formatted:
            return self._tp.fnap(self.main_description_rest_un_formatted)
        else:
            return []

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        from exactly_lib.definitions.entity.actors import all_actor_cross_refs
        return ([concepts.ACTOR_CONCEPT_INFO.cross_reference_target,
                 concepts.SHELL_SYNTAX_CONCEPT_INFO.cross_reference_target]
                +
                all_actor_cross_refs()
                )

    def _command_line_invokation_variants(self) -> List[InvokationVariant]:
        command_line_actor_arg = a.Single(a.Multiplicity.MANDATORY,
                                          a.Option(COMMAND_LINE_ACTOR_OPTION_NAME))
        return [
            invokation_variant_from_args([MANDATORY_EQ_ARG, command_line_actor_arg],
                                         self._description_of_command_line()),
        ]

    def _interpreter_actor_invokation_variants(self,
                                               actor: SingularNameAndCrossReferenceId,
                                               cli_option: a.Single) -> List[InvokationVariant]:
        shell_interpreter_argument = a.Single(a.Multiplicity.MANDATORY,
                                              a.Constant(SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD))
        command_argument = a.Single(a.Multiplicity.MANDATORY, self.command_line_syntax.command)
        executable_arg = a.Single(a.Multiplicity.MANDATORY, self.command_line_syntax.executable)
        optional_arguments_arg = a.Single(a.Multiplicity.ZERO_OR_MORE, self.command_line_syntax.argument)
        return [
            invokation_variant_from_args([MANDATORY_EQ_ARG,
                                          cli_option,
                                          executable_arg,
                                          optional_arguments_arg],
                                         self._description_of_executable_program_interpreter(actor)),
            invokation_variant_from_args([MANDATORY_EQ_ARG,
                                          cli_option,
                                          shell_interpreter_argument,
                                          command_argument],
                                         self._description_of_shell_command_interpreter(actor)),

        ]

    def _description_of_file_interpreter(self) -> List[ParagraphItem]:
        return self._tp.fnap(_DESCRIPTION_OF_FILE_INTERPRETER, {
            'interpreter_actor': formatting.entity(FILE_INTERPRETER_ACTOR.singular_name)
        })

    def _description_of_executable_program_interpreter(self,
                                                       actor: SingularNameAndCrossReferenceId) -> List[ParagraphItem]:
        return self._tp.fnap(_DESCRIPTION_OF_SOURCE_INTERPRETER, {
            'interpreter_actor': formatting.entity(actor.singular_name)
        })

    def _description_of_shell_command_interpreter(self, actor: SingularNameAndCrossReferenceId) -> List[ParagraphItem]:
        return self._tp.fnap(_DESCRIPTION_OF_SHELL_COMMAND_SOURCE_INTERPRETER, {
            'interpreter_actor': formatting.entity(actor.singular_name)
        })

    def _description_of_command_line(self) -> List[ParagraphItem]:
        return self._tp.fnap(_DESCRIPTION_OF_SHELL)


def parse(instruction_argument: str) -> Actor:
    """
    :raises SingleInstructionInvalidArgumentException In case of invalid syntax
    """
    arg = instruction_argument.strip()
    if not arg:
        raise SingleInstructionInvalidArgumentException('An actor must be given')
    try:
        args = arg.split(maxsplit=2)
    except Exception as ex:
        raise SingleInstructionInvalidArgumentException(str(ex))
    if args[0] != instruction_arguments.ASSIGNMENT_OPERATOR:
        raise SingleInstructionInvalidArgumentException('Missing ' +
                                                        instruction_arguments.ASSIGNMENT_OPERATOR)
    del args[0]
    if not args:
        raise SingleInstructionInvalidArgumentException('Missing arguments after ' +
                                                        instruction_arguments.ASSIGNMENT_OPERATOR)
    if matches(COMMAND_LINE_ACTOR_OPTION_NAME, args[0]):
        if len(args) > 1:
            raise SingleInstructionInvalidArgumentException('Superfluous arguments to ' + args[0])
        return command_line.actor()
    if len(args) == 1:
        raise SingleInstructionInvalidArgumentException('Missing file argument for ' + args[0])
    if matches(SOURCE_INTERPRETER_OPTION_NAME, args[0]):
        return _parse_source_interpreter(args[1])
    if matches(FILE_INTERPRETER_OPTION_NAME, args[0]):
        return _parse_file_interpreter(args[1])
    raise SingleInstructionInvalidArgumentException('Invalid option: "{}"'.format(args[0]))


def _parse_source_interpreter(arg: str) -> Actor:
    return source_interpreter.actor(_parse_interpreter_command(arg))


def _parse_file_interpreter(arg: str) -> Actor:
    return file_interpreter.actor(_parse_interpreter_command(arg))


def _parse_interpreter_command(arg: str) -> Command:
    args = arg.split(maxsplit=1)
    if not args:
        raise SingleInstructionInvalidArgumentException('Missing interpreter')
    if args[0] == SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD:
        if len(args) == 1:
            raise SingleInstructionInvalidArgumentException('Missing shell command for interpreter')
        else:
            return commands.shell_command(args[1])
    command_and_arguments = shlex_split(arg)
    if not command_and_arguments:
        raise SingleInstructionInvalidArgumentException('Missing interpreter')
    return commands.system_program_command(command_and_arguments[0],
                                           command_and_arguments[1:])


def shlex_split(s: str) -> list:
    try:
        return shlex.split(s)
    except Exception:
        raise SingleInstructionInvalidArgumentException('Invalid quoting: ' + s)


_DESCRIPTION_OF_FILE_INTERPRETER = """\
Specifies that the {interpreter_actor} {actor} should be used, with an executable program as interpreter.
"""

_DESCRIPTION_OF_SOURCE_INTERPRETER = """\
Specifies that the {interpreter_actor} {actor} should be used, with an executable program as interpreter.
"""

_DESCRIPTION_OF_SHELL_COMMAND_SOURCE_INTERPRETER = """\
Specifies that the {interpreter_actor} {actor} should be used, with a shell command as interpreter.
"""

_DESCRIPTION_OF_SHELL = """\
Specifies that the {command_line_actor} {actor} should be used.
"""
