from enum import Enum
from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.execution.result import ResultBase
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class PartialResultStatus(Enum):
    """
    Implementation notes: integer values must correspond to FullResultStatus
    """
    PASS = 0
    VALIDATION_ERROR = 1
    FAIL = 2
    HARD_ERROR = 99
    IMPLEMENTATION_ERROR = 100


class PartialResult(ResultBase):
    def __init__(self,
                 status: PartialResultStatus,
                 sds: Optional[SandboxDirectoryStructure],
                 failure_info: Optional[FailureInfo]):
        super().__init__(sds, failure_info)
        self.__status = status

    @property
    def status(self) -> PartialResultStatus:
        return self.__status

    @property
    def is_failure(self) -> bool:
        return self.__status is not PartialResultStatus.PASS


def new_partial_result_pass(sds: SandboxDirectoryStructure) -> PartialResult:
    return PartialResult(PartialResultStatus.PASS,
                         sds,
                         None)
