import sys

from exactly_lib.act_phase_setups.source_interpreter import source_file_management
from exactly_lib.act_phase_setups.source_interpreter.executable_file import Constructor
from exactly_lib.act_phase_setups.source_interpreter.source_file_management import StandardSourceFileManager
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling, ActSourceAndExecutorConstructor


def script_language_setup() -> source_file_management.SourceInterpreterSetup:
    return source_file_management.SourceInterpreterSetup(_file_manager())


def _file_manager() -> source_file_management.SourceFileManager:
    if not sys.executable:
        raise ValueError('Cannot execute since name of executable not found in sys.executable.')
    return StandardSourceFileManager('py',
                                     sys.executable,
                                     [])


def new_act_source_and_executor_constructor() -> ActSourceAndExecutorConstructor:
    return Constructor(script_language_setup())


def new_act_phase_handling() -> ActPhaseHandling:
    return ActPhaseHandling(new_act_source_and_executor_constructor())
