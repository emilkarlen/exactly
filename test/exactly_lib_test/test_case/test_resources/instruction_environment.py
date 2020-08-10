from pathlib import Path
from typing import Dict, Callable, Optional

from exactly_lib.common import tmp_dir_file_spaces as std_file_spaces
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep, TmpFileStorage
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatDoNotCreateFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_hds, fake_sds, fake_tcds
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


def fake_pre_sds_environment() -> InstructionEnvironmentForPreSdsStep:
    return InstructionEnvironmentForPreSdsStep(fake_hds(),
                                               ProcessExecutionSettings.with_empty_environ())


def fake_post_sds_environment() -> InstructionEnvironmentForPostSdsStep:
    sds = fake_sds()
    return InstructionEnvironmentForPostSdsStep(
        fake_hds(),
        ProcessExecutionSettings.with_empty_environ(),
        sds,
        TmpFileStorage(sds.internal_tmp_dir / 'instruction-dir',
                       lambda path: DirFileSpaceThatDoNotCreateFiles(path))
    )


def _default_get_tmp_space(root_dir: Path) -> DirFileSpace:
    return std_file_spaces.std_tmp_dir_file_space(root_dir)


class InstructionEnvironmentPostSdsBuilder:
    def __init__(self,
                 hds: HomeDirectoryStructure = fake_hds(),
                 sds: SandboxDirectoryStructure = fake_sds(),
                 environ: Optional[Dict[str, str]] = None,
                 timeout_in_seconds: int = None,
                 symbols: SymbolTable = None,
                 get_paths_access_for_dir:
                 Callable[[Path], DirFileSpace] = _default_get_tmp_space,
                 ):
        self._hds = hds
        self._sds = sds
        self._environ = environ
        self._timeout_in_seconds = timeout_in_seconds
        self._symbols = symbol_table_from_none_or_value(symbols)
        self._get_paths_access_for_dir = get_paths_access_for_dir
        self.get_instr_tmp_file_space = lambda path: TmpFileStorage(path, get_paths_access_for_dir)

    @staticmethod
    def new(hds: HomeDirectoryStructure = fake_hds(),
            environ: Dict[str, str] = None,
            sds: SandboxDirectoryStructure = fake_sds(),
            timeout_in_seconds: int = None,
            symbols: SymbolTable = None
            ) -> 'InstructionEnvironmentPostSdsBuilder':
        return InstructionEnvironmentPostSdsBuilder(
            hds,
            sds,
            environ,
            timeout_in_seconds,
            symbols,
        )

    @staticmethod
    def new_tcds(tcds: Tcds = fake_tcds(),
                 symbols: SymbolTable = None,
                 process_execution_settings: ProcessExecutionSettings = proc_exe_env_for_test(),
                 ) -> 'InstructionEnvironmentPostSdsBuilder':
        return InstructionEnvironmentPostSdsBuilder(
            tcds.hds,
            tcds.sds,
            process_execution_settings.environ,
            process_execution_settings.timeout_in_seconds,
            symbols,
        )

    @staticmethod
    def new_from_pre_sds(
            environment: InstructionEnvironmentForPreSdsStep,
            sds: SandboxDirectoryStructure = fake_sds(),
    ) -> 'InstructionEnvironmentPostSdsBuilder':
        return InstructionEnvironmentPostSdsBuilder(
            environment.hds,
            sds,
            environment.proc_exe_settings.environ,
            environment.proc_exe_settings.timeout_in_seconds,
            environment.symbols,
        )

    def build_pre_sds(self) -> InstructionEnvironmentForPreSdsStep:
        return InstructionEnvironmentForPreSdsStep(
            self._hds,
            ProcessExecutionSettings(self._timeout_in_seconds,
                                     self._environ),
            self._symbols,
        )

    def build_post_sds(self) -> InstructionEnvironmentForPostSdsStep:
        return InstructionEnvironmentForPostSdsStep(
            self._hds,
            ProcessExecutionSettings(self._timeout_in_seconds, self._environ),
            self._sds,
            self.get_instr_tmp_file_space(self._sds.internal_tmp_dir),
            self._symbols,
        )
