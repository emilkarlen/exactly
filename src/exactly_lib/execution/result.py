from enum import Enum

from exactly_lib.execution.phase_step_identifiers.phase_step import PhaseStep
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.failure_details import FailureDetails
from exactly_lib.util.line_source import SourceLocationPath


class FailureInfo:
    def __init__(self,
                 phase_step: PhaseStep,
                 failure_details: FailureDetails,
                 source_location: SourceLocationPath):
        self.__phase_step = phase_step
        self.__failure_details = failure_details
        self.__source_location = source_location

    @property
    def phase_step(self) -> PhaseStep:
        return self.__phase_step

    @property
    def failure_details(self) -> FailureDetails:
        return self.__failure_details

    @property
    def source_location_path(self) -> SourceLocationPath:
        return self.__source_location

    def __str__(self):
        return str(self.phase_step) + ': ' + str(self.failure_details)


class InstructionFailureInfo(FailureInfo):
    """
    Information that is present when an instruction has failed.
    """

    def __init__(self,
                 phase_step: PhaseStep,
                 source_location: SourceLocationPath,
                 failure_details: FailureDetails,
                 element_description: str = None):
        super().__init__(phase_step, failure_details, source_location)
        self.__source_location = source_location
        self.__phase_step = phase_step
        self.__element_description = element_description

    @property
    def source_location(self) -> SourceLocationPath:
        return self.__source_location

    @property
    def element_description(self) -> str:
        return self.__element_description


class PhaseFailureInfo(FailureInfo):
    def __init__(self,
                 phase_step: PhaseStep,
                 failure_details: FailureDetails):
        super().__init__(phase_step, failure_details, None)


class FailureInfoVisitor:
    def visit(self,
              failure_info: FailureInfo):
        if isinstance(failure_info, InstructionFailureInfo):
            return self._visit_instruction_failure(failure_info)
        elif isinstance(failure_info, PhaseFailureInfo):
            return self._visit_phase_failure(failure_info)
        else:
            raise TypeError('Unknown FailureInfo: {}'.format(type(failure_info)))

    def _visit_instruction_failure(self,
                                   failure_info: InstructionFailureInfo):
        raise NotImplementedError()

    def _visit_phase_failure(self,
                             failure_info: PhaseFailureInfo):
        raise NotImplementedError()


class ResultBase:
    def __init__(self,
                 sds: SandboxDirectoryStructure,
                 failure_info: FailureInfo):
        self.__sds = sds
        self.__failure_info = failure_info

    @property
    def has_sds(self) -> bool:
        return self.__sds is not None

    @property
    def sds(self) -> SandboxDirectoryStructure:
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


class PartialResultStatus(Enum):
    """
    Implementation notes: integer values must correspond to FullResultStatus
    """
    PASS = 0
    VALIDATE = 1
    FAIL = 2
    HARD_ERROR = 99
    IMPLEMENTATION_ERROR = 100


class PartialResult(ResultBase):
    def __init__(self,
                 status: PartialResultStatus,
                 sds: SandboxDirectoryStructure,
                 failure_info: FailureInfo):
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


class FullResultStatus(Enum):
    """
    Implementation notes: integer values must correspond to PartialResultStatus
    """
    PASS = 0
    VALIDATE = 1
    FAIL = 2
    SKIPPED = 77
    XFAIL = 4
    XPASS = 5
    HARD_ERROR = 99
    IMPLEMENTATION_ERROR = 100


class FullResult(ResultBase):
    def __init__(self,
                 status: FullResultStatus,
                 sds: SandboxDirectoryStructure,
                 failure_info: FailureInfo):
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
