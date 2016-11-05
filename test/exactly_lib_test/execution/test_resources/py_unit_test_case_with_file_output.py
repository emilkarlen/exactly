import os
import pathlib
import types

from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure


def standard_phase_file_path_eds(sds: SandboxDirectoryStructure,
                                 phase: phase_identifier.PhaseEnum) -> pathlib.Path:
    return standard_phase_file_path(sds.act_dir, phase)


def standard_phase_file_path(test_root_dir: pathlib.Path, phase: phase_identifier.PhaseEnum) -> pathlib.Path:
    return test_root_dir / standard_phase_file_base_name(phase)


def standard_phase_file_base_name(phase: phase_identifier.PhaseEnum) -> str:
    return 'testfile-for-phase-' + phase.name


def write_to_standard_phase_file(phase: phase_identifier.PhaseEnum,
                                 file_lines_from_env: types.FunctionType) -> types.FunctionType:
    def ret_val(environment: common.InstructionEnvironmentForPostSdsStep, *args):
        file_path = standard_phase_file_path(environment.sds.act_dir, phase)
        with open(str(file_path), 'w') as f:
            contents = os.linesep.join(file_lines_from_env(environment)) + os.linesep
            f.write(contents)
        return pfh.new_pfh_pass() if phase is phase_identifier.PhaseEnum.ASSERT else sh.new_sh_success()

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
