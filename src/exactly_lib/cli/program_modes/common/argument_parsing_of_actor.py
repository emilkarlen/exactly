import shlex
from typing import List

from exactly_lib.actors import source_interpreter
from exactly_lib.test_case.actor import Actor
from exactly_lib.type_system.logic.program.process_execution import commands


def resolve_actor_from_argparse_argument(default_actor: Actor,
                                         interpreter: List[str]) -> Actor:
    interpreter_argument = None
    if interpreter and len(interpreter) > 0:
        interpreter_argument = interpreter[0]
    return _resolve_act_phase_setup(default_actor, interpreter_argument)


def _resolve_act_phase_setup(default_actor: Actor,
                             interpreter: str = None) -> Actor:
    if interpreter:
        return _new_for_generic_script_language_setup(interpreter)
    return default_actor


def _new_for_generic_script_language_setup(interpreter: str) -> Actor:
    cmd_and_args = shlex.split(interpreter)
    command = commands.system_program_command(cmd_and_args[0],
                                              cmd_and_args[1:])
    return source_interpreter.actor(command)
