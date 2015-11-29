import os
import pathlib

from shellcheck_lib.execution import phases
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections import common
from shellcheck_lib_test.execution.util.instruction_adapter import InternalInstruction


def standard_phase_file_path_eds(eds: ExecutionDirectoryStructure,
                                 phase: phases.Phase) -> pathlib.Path:
    return standard_phase_file_path(eds.act_dir, phase)


def standard_phase_file_path(test_root_dir: pathlib.Path, phase: phases.Phase) -> pathlib.Path:
    return test_root_dir / standard_phase_file_base_name(phase)


def standard_phase_file_base_name(phase: phases.Phase) -> str:
    return 'testfile-for-phase-' + phase.identifier


class InternalInstructionThatWritesToStandardPhaseFile(InternalInstruction):
    def __init__(self,
                 phase: phases.Phase):
        super().__init__()
        self.__phase = phase

    def execute(self, phase_name: str,
                environment: common.GlobalEnvironmentForPostEdsPhase,
                os_services: OsServices):
        file_path = standard_phase_file_path(environment.eds.act_dir, self.__phase)
        with open(str(file_path), 'w') as f:
            contents = os.linesep.join(self._file_lines(environment)) + os.linesep
            f.write(contents)

    def _file_lines(self,
                    environment: common.GlobalEnvironmentForPostEdsPhase) -> list:
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
