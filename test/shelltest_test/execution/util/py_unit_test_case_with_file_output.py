import os
import pathlib

from shelltest.execution.execution_directory_structure import ExecutionDirectoryStructure
from shelltest import phases
from shelltest.exec_abs_syn import instructions


def standard_phase_file_path_eds(eds: ExecutionDirectoryStructure,
                                 phase: phases.Phase) -> pathlib.Path:
    return standard_phase_file_path(eds.test_root_dir, phase)


def standard_phase_file_path(test_root_dir: pathlib.Path, phase: phases.Phase) -> pathlib.Path:
    return test_root_dir / standard_phase_file_base_name(phase)


def standard_phase_file_base_name(phase: phases.Phase) -> str:
    return 'testfile-for-phase-' + phase.name


class InternalInstructionThatWritesToStandardPhaseFile(instructions.InternalInstruction):
    def __init__(self,
                 phase: phases.Phase):
        super().__init__()
        self.__phase = phase

    def execute(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForInternalCommands):
        file_path = standard_phase_file_path(global_environment.eds.test_root_dir, self.__phase)
        with open(str(file_path), 'w') as f:
            contents = os.linesep.join(self._file_lines(global_environment)) + os.linesep
            f.write(contents)

    def _file_lines(self, global_environment: instructions.GlobalEnvironmentForNamedPhase) -> list:
        raise NotImplementedError()


class ModulesAndStatements:
    def __init__(self,
                 used_modules: set,
                 statements: list):
        self.__used_modules = used_modules
        self.__statements = statements

    @property
    def used_modules(self) -> set:
        return self.__used_modules

    @property
    def statements(self) -> list:
        return self.__statements
