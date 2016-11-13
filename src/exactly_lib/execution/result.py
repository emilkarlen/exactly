from enum import Enum

from exactly_lib.execution.phase_step_identifiers.phase_step import PhaseStep
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util import line_source
from exactly_lib.util.failure_details import FailureDetails


class FailureInfo:
    def __init__(self,
                 phase_step: PhaseStep,
                 failure_details: FailureDetails):
        self.__phase_step = phase_step
        self.__failure_details = failure_details

    @property
    def phase_step(self) -> PhaseStep:
        return self.__phase_step

    @property
    def failure_details(self) -> FailureDetails:
        return self.__failure_details

    def __str__(self):
        return str(self.phase_step) + ': ' + str(self.failure_details)

class InstructionFailureInfo(FailureInfo):
    """
    Information that is present when an instruction has failed.
    """

    def __init__(self,
                 phase_step: PhaseStep,
                 source_line: line_source.Line,
                 failure_details: FailureDetails):
        super().__init__(phase_step, failure_details)
        self.__source_line = source_line
        self.__phase_step = phase_step

    @property
    def source_line(self) -> line_source.Line:
        return self.__source_line


class PhaseFailureInfo(FailureInfo):
    def __init__(self,
                 phase_step: PhaseStep,
                 failure_details: FailureDetails):
        super().__init__(phase_step, failure_details)


class FailureInfoVisitor:
    def visit(self,
              failure_info: FailureInfo):
        if isinstance(failure_info, InstructionFailureInfo):
            return self._visit_instruction_failure(failure_info)
        elif isinstance(failure_info, PhaseFailureInfo):
            return self._visit_phase_failure(failure_info)
        else:
            raise ValueError('Unknown FailureInfo: {}'.format(type(failure_info)))

    def _visit_instruction_failure(self,
                                   failure_info: InstructionFailureInfo):
        raise NotImplementedError()

    def _visit_phase_failure(self,
                             failure_info: PhaseFailureInfo):
        raise NotImplementedError()


class ResultBase:
    def __init__(self,
                 sandbox_directory_structure: SandboxDirectoryStructure,
                 failure_info: FailureInfo):
        self.__sandbox_directory_structure = sandbox_directory_structure
        self.__failure_info = failure_info

    @property
    def has_sandbox_directory_structure(self) -> bool:
        return self.__sandbox_directory_structure is not None

    @property
    def sandbox_directory_structure(self) -> SandboxDirectoryStructure:
        return self.__sandbox_directory_structure

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
                 sandbox_directory_structure: SandboxDirectoryStructure,
                 failure_info: FailureInfo):
        super().__init__(sandbox_directory_structure, failure_info)
        self.__status = status

    @property
    def status(self) -> PartialResultStatus:
        return self.__status

    @property
    def is_failure(self) -> bool:
        return self.__status is not PartialResultStatus.PASS


def new_partial_result_pass(sandbox_directory_structure: SandboxDirectoryStructure) -> PartialResult:
    return PartialResult(PartialResultStatus.PASS,
                         sandbox_directory_structure,
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
                 sandbox_directory_structure: SandboxDirectoryStructure,
                 failure_info: FailureInfo):
        super().__init__(sandbox_directory_structure, failure_info)
        self.__status = status

    @property
    def status(self) -> FullResultStatus:
        return self.__status


def new_skipped() -> FullResult:
    return FullResult(FullResultStatus.SKIPPED,
                      None,
                      None)


def new_pass(sandbox_directory_structure: SandboxDirectoryStructure) -> FullResult:
    return FullResult(FullResultStatus.PASS,
                      sandbox_directory_structure,
                      None)
