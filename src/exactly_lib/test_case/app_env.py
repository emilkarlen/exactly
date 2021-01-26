from exactly_lib.test_case.os_services import OsServices
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


class ApplicationEnvironment:
    def __init__(self,
                 os_services: OsServices,
                 process_execution_settings: ProcessExecutionSettings,
                 tmp_files_space: DirFileSpace,
                 mem_buff_size: int,
                 ):
        self._os_services = os_services
        self._process_execution_settings = process_execution_settings
        self._tmp_files_space = tmp_files_space
        self._mem_buff_size = mem_buff_size

    @property
    def tmp_files_space(self) -> DirFileSpace:
        return self._tmp_files_space

    @property
    def mem_buff_size(self) -> int:
        return self._mem_buff_size

    @property
    def os_services(self) -> OsServices:
        return self._os_services

    @property
    def process_execution_settings(self) -> ProcessExecutionSettings:
        return self._process_execution_settings
