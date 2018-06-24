from enum import Enum
from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.execution.partial_execution.result import PartialExeResult, PartialExeResultStatus
from exactly_lib.execution.result import ResultBase, ActionToCheckOutcome
from exactly_lib.test_case.test_case_status import TestCaseStatus
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class FullExeResultStatus(Enum):
    """
    Implementation notes: integer values must correspond to PartialExeResultStatus
    """
    PASS = 0
    VALIDATION_ERROR = 1
    FAIL = 2
    SKIPPED = 77
    XFAIL = 4
    XPASS = 5
    HARD_ERROR = 99
    IMPLEMENTATION_ERROR = 100


class FullExeResult(ResultBase):
    """The result of a full execution"""

    def __init__(self,
                 status: FullExeResultStatus,
                 sds: Optional[SandboxDirectoryStructure],
                 action_to_check_outcome: Optional[ActionToCheckOutcome],
                 failure_info: Optional[FailureInfo]):
        super().__init__(sds, action_to_check_outcome, failure_info)
        self.__status = status

    @property
    def status(self) -> FullExeResultStatus:
        return self.__status


def new_skipped() -> FullExeResult:
    return FullExeResult(FullExeResultStatus.SKIPPED,
                         None,
                         None,
                         None)


def new_pass(sds: SandboxDirectoryStructure,
             action_to_check_outcome: ActionToCheckOutcome) -> FullExeResult:
    return FullExeResult(FullExeResultStatus.PASS,
                         sds,
                         action_to_check_outcome,
                         None)


def new_from_result_of_partial_execution(execution_mode: TestCaseStatus,
                                         partial_result: PartialExeResult) -> FullExeResult:
    return FullExeResult(translate_status(execution_mode, partial_result.status),
                         partial_result.sds,
                         partial_result.action_to_check_outcome,
                         partial_result.failure_info)


def translate_status(execution_mode: TestCaseStatus,
                     ps: PartialExeResultStatus) -> FullExeResultStatus:
    """
    :param execution_mode: Must not be ExecutionMode.SKIPPED
    """
    if execution_mode is TestCaseStatus.FAIL:
        if ps is PartialExeResultStatus.FAIL:
            return FullExeResultStatus.XFAIL
        elif ps is PartialExeResultStatus.PASS:
            return FullExeResultStatus.XPASS
    return FullExeResultStatus(ps.value)
