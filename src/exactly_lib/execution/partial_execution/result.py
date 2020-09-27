from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.execution.result import ResultBase, ActionToCheckOutcome, ExecutionFailureStatus
from exactly_lib.tcfs.sds import SandboxDs


class PartialExeResult(ResultBase):
    """The result of a partial execution"""

    def __init__(self,
                 status: Optional[ExecutionFailureStatus],
                 sds: Optional[SandboxDs],
                 action_to_check_outcome: Optional[ActionToCheckOutcome],
                 failure_info: Optional[FailureInfo]):
        super().__init__(sds, action_to_check_outcome, failure_info)
        self.__status = status

    @property
    def status(self) -> Optional[ExecutionFailureStatus]:
        return self.__status
