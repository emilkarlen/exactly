import shlex
from typing import List

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.parse.shell_syntax import SHELL_KEYWORD
from exactly_lib.type_system.logic.program.process_execution import commands
from exactly_lib.type_system.logic.program.process_execution.command import Command

SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD = SHELL_KEYWORD
_MISSING_INTERPRETER_MSG = 'Missing ' + syntax_elements.ACT_INTERPRETER_SYNTAX_ELEMENT.singular_name


def parse(arg: str) -> Command:
    args = arg.split(maxsplit=1)
    if not args:
        raise SingleInstructionInvalidArgumentException(_MISSING_INTERPRETER_MSG)
    if args[0] == SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD:
        if len(args) == 1:
            raise SingleInstructionInvalidArgumentException('Missing shell command for interpreter')
        else:
            return commands.shell_command(args[1])
    command_and_arguments = shlex_split(arg)
    if not command_and_arguments:
        raise SingleInstructionInvalidArgumentException(_MISSING_INTERPRETER_MSG)
    return commands.system_program_command(command_and_arguments[0],
                                           command_and_arguments[1:])


def shlex_split(s: str) -> List[str]:
    try:
        return shlex.split(s)
    except Exception:
        raise SingleInstructionInvalidArgumentException('Invalid quoting: ' + s)
