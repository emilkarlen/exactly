from enum import Enum
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


class FullResultStatus(Enum):
    """
    Implementation notes: integer values must correspond to PartialResultStatus
    """
    PASS = 0
    VALIDATION_ERROR = 1
    FAIL = 2
    SKIPPED = 77
    XFAIL = 4
    XPASS = 5
    HARD_ERROR = 99
    IMPLEMENTATION_ERROR = 100


class FullResult(ResultBase):
    def __init__(self,
                 status: FullResultStatus,
                 sds: Optional[SandboxDirectoryStructure],
                 failure_info: Optional[FailureInfo]):
        super().__init__(sds, failure_info)
        self.__status = status

    @property
    def status(self) -> FullResultStatus:
        return self.__status


def new_skipped() -> FullResult:
    return FullResult(FullResultStatus.SKIPPED,
                      None,
                      None)


def new_pass(sds: SandboxDirectoryStructure) -> FullResult:
    return FullResult(FullResultStatus.PASS,
                      sds,
                      None)
