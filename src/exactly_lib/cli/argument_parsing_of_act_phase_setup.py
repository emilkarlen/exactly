import shlex

from exactly_lib.act_phase_setups.source_interpreter import act_phase_setup
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.util.process_execution.os_process_execution import Command


def resolve_act_phase_setup_from_argparse_argument(default_setup: ActPhaseSetup,
                                                   interpreter: list) -> ActPhaseSetup:
    interpreter_argument = None
    if interpreter and len(interpreter) > 0:
        interpreter_argument = interpreter[0]
    return _resolve_act_phase_setup(default_setup, interpreter_argument)


def _resolve_act_phase_setup(default_setup: ActPhaseSetup,
                             interpreter: str = None) -> ActPhaseSetup:
    if interpreter:
        return _new_for_generic_script_language_setup(interpreter)
    return default_setup


def _new_for_generic_script_language_setup(interpreter: str) -> ActPhaseSetup:
    cmd_and_args = shlex.split(interpreter)
    command = Command(cmd_and_args, shell=False)
    return act_phase_setup(command)
