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


class ActionToCheckOutcome(tuple):
    def __new__(cls,
                exit_code: int):
        return tuple.__new__(cls, (exit_code,))

    @property
    def exit_code(self) -> int:
        return self[0]


class PartialResult(ResultBase):
    def __init__(self,
                 status: PartialResultStatus,
                 sds: Optional[SandboxDirectoryStructure],
                 action_to_check_outcome: Optional[ActionToCheckOutcome],
                 failure_info: Optional[FailureInfo]):
        super().__init__(sds, failure_info)
        self.__status = status
        self.__action_to_check_outcome = action_to_check_outcome

    @property
    def status(self) -> PartialResultStatus:
        return self.__status

    @property
    def has_action_to_check_outcome(self) -> bool:
        return self.__action_to_check_outcome is not None

    @property
    def action_to_check_outcome(self) -> Optional[ActionToCheckOutcome]:
        """
        :return: Not None iff Action To Check has been completely executed
        """
        return self.__action_to_check_outcome
