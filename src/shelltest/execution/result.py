from enum import Enum

from shelltest.execution.phase_step import PhaseStep
from shelltest.phase_instr import line_source
from .execution_directory_structure import ExecutionDirectoryStructure


class InstructionFailureDetails:
    """
    EITHER an error message OR an exception
    """

    def __init__(self,
                 failure_message: str,
                 exception: Exception):
        self.__failure_message = failure_message
        self.__exception = exception
        if self.__failure_message is None:
            if self.__exception is None:
                raise ValueError('Must specify either an error_message or an exception')
        else:
            if self.__exception is not None:
                raise ValueError('Must specify either an error_message or an exception - not both')

    @property
    def is_error_message(self) -> bool:
        return self.__failure_message is not None

    @property
    def failure_message(self) -> str:
        return self.__failure_message

    @property
    def exception(self) -> Exception:
        return self.__exception


def new_failure_details_from_exception(exception: Exception) -> InstructionFailureDetails:
    return InstructionFailureDetails(None, exception)


def new_failure_details_from_message(error_message: str) -> InstructionFailureDetails:
    return InstructionFailureDetails(error_message, None)


class InstructionFailureInfo:
    """
    Information that is present when an instruction has failed.
    """

    def __init__(self,
                 phase_step: PhaseStep,
                 source_line: line_source.Line,
                 failure_details: InstructionFailureDetails):
        self.__source_line = source_line
        self.__phase_step = phase_step
        self.__failure_details = failure_details

    @property
    def source_line(self) -> line_source.Line:
        return self.__source_line

    @property
    def phase_step(self) -> PhaseStep:
        return self.__phase_step

    @property
    def failure_details(self) -> InstructionFailureDetails:
        return self.__failure_details


class ResultBase:
    def __init__(self,
                 execution_directory_structure: ExecutionDirectoryStructure,
                 instruction_failure_info: InstructionFailureInfo):
        self.__execution_directory_structure = execution_directory_structure
        self.__instruction_failure_info = instruction_failure_info

    @property
    def has_execution_directory_structure(self) -> bool:
        return self.__execution_directory_structure is not None

    @property
    def execution_directory_structure(self) -> ExecutionDirectoryStructure:
        return self.__execution_directory_structure

    @property
    def is_instruction_failure(self) -> bool:
        return self.__instruction_failure_info is not None

    @property
    def instruction_failure_info(self) -> InstructionFailureInfo:
        """
        Precondition: is_instruction_failure
        """
        return self.__instruction_failure_info


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
                 execution_directory_structure: ExecutionDirectoryStructure,
                 instruction_failure_info: InstructionFailureInfo):
        super().__init__(execution_directory_structure, instruction_failure_info)
        self.__status = status

    @property
    def status(self) -> PartialResultStatus:
        return self.__status

    @property
    def is_failure(self) -> bool:
        return self.__status is not PartialResultStatus.PASS


def new_partial_result_pass(execution_directory_structure: ExecutionDirectoryStructure) -> PartialResult:
    return PartialResult(PartialResultStatus.PASS,
                         execution_directory_structure,
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
                 execution_directory_structure: ExecutionDirectoryStructure,
                 instruction_failure_info: InstructionFailureInfo):
        super().__init__(execution_directory_structure, instruction_failure_info)
        self.__status = status

    @property
    def status(self) -> FullResultStatus:
        return self.__status


def new_skipped() -> FullResult:
    return FullResult(FullResultStatus.SKIPPED,
                      None,
                      None)
