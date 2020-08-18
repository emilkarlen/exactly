import shlex
from typing import List

from exactly_lib.actors import source_interpreter
from exactly_lib.definitions.entity import actors
from exactly_lib.test_case.actor import Actor
from exactly_lib.type_system.logic.program.process_execution import commands
from exactly_lib.util.name_and_value import NameAndValue


def resolve_actor_from_argparse_argument(default_actor: NameAndValue[Actor],
                                         interpreter: List[str]) -> NameAndValue[Actor]:
    interpreter_argument = None
    if interpreter and len(interpreter) > 0:
        interpreter_argument = interpreter[0]
    return _resolve_act_phase_setup(default_actor, interpreter_argument)


def _resolve_act_phase_setup(default_actor: NameAndValue[Actor],
                             interpreter: str = None) -> NameAndValue[Actor]:
    if interpreter:
        return _new_for_generic_script_language_setup(interpreter)
    return default_actor


def _new_for_generic_script_language_setup(interpreter: str) -> NameAndValue[Actor]:
    cmd_and_args = shlex.split(interpreter)
    command = commands.system_program_command(cmd_and_args[0],
                                              cmd_and_args[1:])
    return NameAndValue(actors.SOURCE_INTERPRETER_ACTOR.singular_name,
                        source_interpreter.actor(command))
