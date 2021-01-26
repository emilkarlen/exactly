from typing import List, Optional

from exactly_lib.cli.definitions import common_cli_options
from exactly_lib.cli.program_modes.common.shlex_arg_parse import shlex_split
from exactly_lib.definitions.entity import actors
from exactly_lib.impls.actors.source_interpreter import actor
from exactly_lib.impls.types.program.command import command_sdvs
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.util.name_and_value import NameAndValue


def resolve_actor_from_argparse_argument(default_actor: NameAndValue[Actor],
                                         interpreter: Optional[List[str]]) -> NameAndValue[Actor]:
    if not interpreter:
        return default_actor

    interpreter_cmd_and_args = shlex_split(common_cli_options.OPTION_FOR_ACTOR__LONG, interpreter[0])

    return _source_interpreter_with_system_command(interpreter_cmd_and_args)


def _source_interpreter_with_system_command(cmd_and_args: List[str]) -> NameAndValue[Actor]:
    command_sdv = command_sdvs.for_system_program(
        string_sdvs.str_constant(cmd_and_args[0]),
        ArgumentsSdv(list_sdvs.from_str_constants(cmd_and_args[1:])),
    )
    return NameAndValue(actors.SOURCE_INTERPRETER_ACTOR.singular_name,
                        actor.actor(command_sdv))
