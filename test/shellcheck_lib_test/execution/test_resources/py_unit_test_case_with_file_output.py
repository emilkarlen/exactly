import os
import pathlib
import types

from shellcheck_lib.execution import phases
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.test_case.sections import common
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh


def standard_phase_file_path_eds(eds: ExecutionDirectoryStructure,
                                 phase: phases.PhaseEnum) -> pathlib.Path:
    return standard_phase_file_path(eds.act_dir, phase)


def standard_phase_file_path(test_root_dir: pathlib.Path, phase: phases.PhaseEnum) -> pathlib.Path:
    return test_root_dir / standard_phase_file_base_name(phase)


def standard_phase_file_base_name(phase: phases.PhaseEnum) -> str:
    return 'testfile-for-phase-' + phase.name


def write_to_standard_phase_file(phase: phases.PhaseEnum,
                                 file_lines_from_env: types.FunctionType) -> types.FunctionType:
    def ret_val(environment: common.GlobalEnvironmentForPostEdsPhase, *args):
        file_path = standard_phase_file_path(environment.eds.act_dir, phase)
        with open(str(file_path), 'w') as f:
            contents = os.linesep.join(file_lines_from_env(environment)) + os.linesep
            f.write(contents)
        return pfh.new_pfh_pass() if phase is phases.PhaseEnum.ASSERT else sh.new_sh_success()

    return ret_val


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
