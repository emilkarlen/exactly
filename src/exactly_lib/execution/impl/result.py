from typing import Optional

from exactly_lib.execution.failure_info import FailureInfo
from exactly_lib.execution.partial_execution.result import PartialResultStatus
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.failure_details import FailureDetails
from exactly_lib.util.line_source import SourceLocationPath


class Failure(tuple):
    def __new__(cls,
                status: PartialResultStatus,
                source_location: SourceLocationPath,
                failure_details: FailureDetails,
                element_description: str = None):
        """
        :param source_location: None if no source is related to the failure.
        """
        return tuple.__new__(cls, (status, source_location, failure_details, element_description))

    @property
    def status(self) -> PartialResultStatus:
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
                 status: PartialResultStatus,
                 sds: Optional[SandboxDirectoryStructure],
                 failure_info: Optional[FailureInfo]):
        self.__sds = sds
        self.__failure_info = failure_info
        self.__status = status

    @property
    def has_sds(self) -> bool:
        return self.__sds is not None

    @property
    def sds(self) -> Optional[SandboxDirectoryStructure]:
        return self.__sds

    @property
    def failure_info(self) -> Optional[FailureInfo]:
        return self.__failure_info

    @property
    def status(self) -> PartialResultStatus:
        return self.__status
