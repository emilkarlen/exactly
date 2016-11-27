from exactly_lib.act_phase_setups.source_interpreter import python3
from exactly_lib.act_phase_setups.source_interpreter import script_language_management
from exactly_lib.act_phase_setups.source_interpreter.script_language_management import ScriptLanguageSetup
from exactly_lib.act_phase_setups.source_interpreter.script_language_setup import new_for_script_language_setup
from exactly_lib.processing.act_phase import ActPhaseSetup

INTERPRETER_FOR_TEST = 'test-language'


def resolve_act_phase_setup_from_argparse_argument(default_setup: ActPhaseSetup,
                                                   interpreter: list) -> ActPhaseSetup:
    interpreter_argument = None
    if interpreter and len(interpreter) > 0:
        interpreter_argument = interpreter[0]
    return resolve_act_phase_setup(default_setup, interpreter_argument)


def resolve_act_phase_setup(default_setup: ActPhaseSetup,
                            interpreter: str = None) -> ActPhaseSetup:
    if interpreter:
        if interpreter == INTERPRETER_FOR_TEST:
            return python3.new_act_phase_setup()
        else:
            return new_for_generic_script_language_setup(interpreter)
    return default_setup


def new_for_generic_script_language_setup(interpreter: str) -> ActPhaseSetup:
    return new_for_script_language_setup(
        ScriptLanguageSetup(script_language_management.StandardScriptFileManager(
            'src',
            interpreter,
            [])))
