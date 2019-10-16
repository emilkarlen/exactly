from typing import Callable

from exactly_lib.execution.result import ExecutionFailureStatus
from exactly_lib.section_document.source_location import SourceLocationPath
from exactly_lib.test_case.result.failure_details import FailureDetails


class Failure(tuple):
    def __new__(cls,
                status: ExecutionFailureStatus,
                source_location: SourceLocationPath,
                failure_details: FailureDetails,
                element_description: str = None):
        """
        :param source_location: None if no source is related to the failure.
        """
        return tuple.__new__(cls, (status, source_location, failure_details, element_description))

    @property
    def status(self) -> ExecutionFailureStatus:
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


ActionThatRaisesPhaseStepFailureException = Callable[[], None]
