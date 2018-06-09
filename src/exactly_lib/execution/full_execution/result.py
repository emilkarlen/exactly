from enum import Enum
from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.execution.partial_execution.result import PartialResult, PartialResultStatus
from exactly_lib.execution.result import ResultBase
from exactly_lib.test_case.test_case_status import ExecutionMode
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


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


def new_configuration_phase_failure_from(partial_result: PartialResult) -> FullResult:
    full_status = FullResultStatus.HARD_ERROR
    if partial_result.status is PartialResultStatus.IMPLEMENTATION_ERROR:
        full_status = FullResultStatus.IMPLEMENTATION_ERROR
    return FullResult(full_status,
                      None,
                      partial_result.failure_info)


def new_named_phases_result_from(execution_mode: ExecutionMode,
                                 partial_result: PartialResult) -> FullResult:
    return FullResult(translate_status(execution_mode, partial_result.status),
                      partial_result.sds,
                      partial_result.failure_info)


def translate_status(execution_mode: ExecutionMode,
                     ps: PartialResultStatus) -> FullResultStatus:
    """
    :param execution_mode: Must not be ExecutionMode.SKIPPED
    """
    if execution_mode is ExecutionMode.FAIL:
        if ps is PartialResultStatus.FAIL:
            return FullResultStatus.XFAIL
        elif ps is PartialResultStatus.PASS:
            return FullResultStatus.XPASS
    return FullResultStatus(ps.value)
