import sys

from exactly_lib.act_phase_setups.source_interpreter import script_language_management
from exactly_lib.act_phase_setups.source_interpreter.interpreter_setup import new_for_script_language_setup
from exactly_lib.act_phase_setups.source_interpreter.script_language_management import StandardScriptFileManager
from exactly_lib.processing.act_phase import ActPhaseSetup


def script_language_setup() -> script_language_management.ScriptLanguageSetup:
    return script_language_management.ScriptLanguageSetup(_file_manager())


def _file_manager() -> script_language_management.ScriptFileManager:
    if not sys.executable:
        raise ValueError('Cannot execute since name of executable not found in sys.executable.')
    return StandardScriptFileManager('py',
                                     sys.executable,
                                     [])


def new_act_phase_setup() -> ActPhaseSetup:
    return new_for_script_language_setup(script_language_setup())
