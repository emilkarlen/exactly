from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class ResultBase:
    def __init__(self,
                 sds: Optional[SandboxDirectoryStructure],
                 failure_info: Optional[FailureInfo]):
        self.__sds = sds
        self.__failure_info = failure_info

    @property
    def has_sds(self) -> bool:
        return self.__sds is not None

    @property
    def sds(self) -> Optional[SandboxDirectoryStructure]:
        return self.__sds

    @property
    def is_failure(self) -> bool:
        return self.__failure_info is not None

    @property
    def failure_info(self) -> FailureInfo:
        """
        Precondition: is_failure
        """
        return self.__failure_info
