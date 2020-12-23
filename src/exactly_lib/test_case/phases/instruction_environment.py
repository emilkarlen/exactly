from pathlib import Path
from typing import Callable

from exactly_lib.tcfs import sds as _sds
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.util.file_utils import ensure_file_existence
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable


class InstructionEnvironmentForPreSdsStep:
    def __init__(self,
                 hds: HomeDs,
                 proc_exe_settings: ProcessExecutionSettings,
                 symbols: SymbolTable,
                 mem_buff_size: int,
                 ):
        if symbols is None:
            raise ValueError('symbols is None')
        self._hds = hds
        self._symbols = symbols
        self._proc_exe_settings = proc_exe_settings
        self._mem_buff_size = mem_buff_size

    @property
    def hds(self) -> HomeDs:
        return self._hds

    @property
    def proc_exe_settings(self) -> ProcessExecutionSettings:
        return self._proc_exe_settings

    @property
    def symbols(self) -> SymbolTable:
        return self._symbols

    @property
    def mem_buff_size(self) -> int:
        return self._mem_buff_size

    @property
    def path_resolving_environment(self) -> PathResolvingEnvironmentPreSds:
        return PathResolvingEnvironmentPreSds(self._hds, self._symbols)


class TmpFileStorage:
    def __init__(self,
                 root_dir__may_not_exist: Path,
                 get_paths_access_for_dir: Callable[[Path], DirFileSpace]
                 ):
        self._root_dir__may_not_exist = root_dir__may_not_exist
        self._root_dir__existing = None
        self._paths_access_for_dir = get_paths_access_for_dir(root_dir__may_not_exist)

    @property
    def root_dir__may_not_exist(self) -> Path:
        return self._root_dir__may_not_exist

    @property
    def root_dir__existing(self) -> Path:
        if self._root_dir__existing is None:
            ensure_file_existence.ensure_directory_exists_as_a_directory__impl_error(self._root_dir__may_not_exist)
            self._root_dir__existing = self._root_dir__may_not_exist

        return self._root_dir__may_not_exist

    @property
    def paths_access(self) -> DirFileSpace:
        return self._paths_access_for_dir


class InstructionEnvironmentForPostSdsStep(InstructionEnvironmentForPreSdsStep):
    def __init__(self,
                 hds: HomeDs,
                 proc_exe_settings: ProcessExecutionSettings,
                 sds: _sds.SandboxDs,
                 tmp_dir_space: TmpFileStorage,
                 symbols: SymbolTable,
                 mem_buff_size: int,
                 ):
        super().__init__(hds, proc_exe_settings, symbols, mem_buff_size)
        self._tmp_dir_space = tmp_dir_space
        self._sds = sds

    @property
    def sds(self) -> _sds.SandboxDs:
        return self._sds

    @property
    def tcds(self) -> TestCaseDs:
        return TestCaseDs(self.hds,
                          self.sds)

    @property
    def tmp_dir__path_access(self) -> TmpFileStorage:
        return self._tmp_dir_space

    @property
    def path_resolving_environment(self) -> PathResolvingEnvironmentPostSds:
        return PathResolvingEnvironmentPostSds(self._sds, self.symbols)

    @property
    def path_resolving_environment_pre_or_post_sds(self) -> PathResolvingEnvironmentPreOrPostSds:
        return PathResolvingEnvironmentPreOrPostSds(self.tcds, self.symbols)
