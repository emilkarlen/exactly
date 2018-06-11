from typing import Callable, Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.execution.partial_execution.result import PartialExeResultStatus
from exactly_lib.util.failure_details import FailureDetails
from exactly_lib.util.line_source import SourceLocationPath


class Failure(tuple):
    def __new__(cls,
                status: PartialExeResultStatus,
                source_location: SourceLocationPath,
                failure_details: FailureDetails,
                element_description: str = None):
        """
        :param source_location: None if no source is related to the failure.
        """
        return tuple.__new__(cls, (status, source_location, failure_details, element_description))

    @property
    def status(self) -> PartialExeResultStatus:
        return self[0]

    @property
    def source_location(self) -> SourceLocationPath:
        """
        :return: None if no source is related to the failure.
        """
        return self[1]

    @property
    def failure_details(self) -> FailureDetails:
        return self[2]

    @property
    def element_description(self) -> str:
        """
        :return: May be None
        """
        return self[3]


class PhaseStepFailure:
    def __init__(self,
                 status: PartialExeResultStatus,
                 failure_info: FailureInfo):
        """

        :param status: Must not be PASS
        :param failure_info:
        """
        self.__failure_info = failure_info
        self.__status = status

    @property
    def status(self) -> PartialExeResultStatus:
        return self.__status

    @property
    def failure_info(self) -> FailureInfo:
        return self.__failure_info


ActionWithFailureAsResult = Callable[[], Optional[PhaseStepFailure]]
