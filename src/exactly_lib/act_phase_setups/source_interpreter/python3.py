import sys

from exactly_lib.act_phase_setups.source_interpreter import source_file_management
from exactly_lib.act_phase_setups.source_interpreter.interpreter_setup import new_for_script_language_setup
from exactly_lib.act_phase_setups.source_interpreter.source_file_management import StandardSourceFileManager
from exactly_lib.processing.act_phase import ActPhaseSetup


def script_language_setup() -> source_file_management.SourceInterpreterSetup:
    return source_file_management.SourceInterpreterSetup(_file_manager())


def _file_manager() -> source_file_management.SourceFileManager:
    if not sys.executable:
        raise ValueError('Cannot execute since name of executable not found in sys.executable.')
    return StandardSourceFileManager('py',
                                     sys.executable,
                                     [])


def new_act_phase_setup() -> ActPhaseSetup:
    return new_for_script_language_setup(script_language_setup())
