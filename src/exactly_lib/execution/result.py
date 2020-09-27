from enum import Enum
from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.tcfs.sds import SandboxDs


class ExecutionFailureStatus(Enum):
    """
    Implementation notes: integer values must correspond to FullExeResultStatus
    """
    SYNTAX_ERROR = 3
    VALIDATION_ERROR = 1
    FAIL = 2
    HARD_ERROR = 99
    INTERNAL_ERROR = 100


class ActionToCheckOutcome(tuple):
    def __new__(cls,
                exit_code: int):
        return tuple.__new__(cls, (exit_code,))

    @property
    def exit_code(self) -> int:
        return self[0]


class ResultBase:
    def __init__(self,
                 sds: Optional[SandboxDs],
                 action_to_check_outcome: Optional[ActionToCheckOutcome],
                 failure_info: Optional[FailureInfo]):
        self.__sds = sds
        self.__action_to_check_outcome = action_to_check_outcome
        self.__failure_info = failure_info

    @property
    def has_sds(self) -> bool:
        return self.__sds is not None

    @property
    def sds(self) -> Optional[SandboxDs]:
        return self.__sds

    @property
    def has_action_to_check_outcome(self) -> bool:
        return self.__action_to_check_outcome is not None

    @property
    def action_to_check_outcome(self) -> Optional[ActionToCheckOutcome]:
        """
        :return: Not None iff Action To Check has been completely executed
        """
        return self.__action_to_check_outcome

    @property
    def is_failure(self) -> bool:
        return self.__failure_info is not None

    @property
    def failure_info(self) -> Optional[FailureInfo]:
        return self.__failure_info


class PhaseStepFailure:
    def __init__(self,
                 status: ExecutionFailureStatus,
                 failure_info: FailureInfo):
        """
        :param failure_info:
        """
        self.__failure_info = failure_info
        self.__status = status

    @property
    def status(self) -> ExecutionFailureStatus:
        return self.__status

    @property
    def failure_info(self) -> FailureInfo:
        return self.__failure_info


class PhaseStepFailureException(Exception):
    def __init__(self, failure: PhaseStepFailure):
        self.failure = failure
