import sys

from exactly_lib.act_phase_setups.source_interpreter import source_file_management
from exactly_lib.act_phase_setups.source_interpreter.executable_file import Parser
from exactly_lib.act_phase_setups.source_interpreter.source_file_management import StandardSourceFileManager
from exactly_lib.test_case.actor import ActionToCheckExecutorParser


def source_interpreter_setup() -> source_file_management.SourceInterpreterSetup:
    return source_file_management.SourceInterpreterSetup(_file_manager())


def _file_manager() -> source_file_management.SourceFileManager:
    if not sys.executable:
        raise ValueError('Cannot execute since name of executable not found in sys.executable.')
    return StandardSourceFileManager('py',
                                     sys.executable,
                                     [])


def new_atc_executor_parser() -> ActionToCheckExecutorParser:
    return Parser(source_interpreter_setup())


def new_actor() -> ActionToCheckExecutorParser:
    return new_atc_executor_parser()
