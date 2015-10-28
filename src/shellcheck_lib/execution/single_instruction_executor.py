from enum import Enum

from shellcheck_lib.execution import result
from shellcheck_lib.execution.result import FailureDetails, PartialResultStatus
from shellcheck_lib.general import line_source
from shellcheck_lib.document.model import Instruction, PhaseContentElement


class PartialControlledFailureEnum(Enum):
    """
    Implementation notes: integer values must correspond to PartialResultStatus

    "controlled" means that implementation errors are not handled.
    """
    VALIDATION = 1
    FAIL = 2
    HARD_ERROR = 99


class PartialInstructionControlledFailureInfo(tuple):
    """
    "controlled" means that implementation errors are not handled.
    """

    def __new__(cls,
                partial_controlled_failure_enum: PartialControlledFailureEnum,
                error_message: str):
        return tuple.__new__(cls, (partial_controlled_failure_enum,
                                   error_message))

    @property
    def status(self) -> PartialControlledFailureEnum:
        return self[0]

    @property
    def error_message(self) -> str:
        return self[1]


class ControlledInstructionExecutor:
    """
    Capable of executes a single step of any instruction of a single type.
    The object knows which method of the instruction to invoke, and also
    the arguments to pass.
    It is able to execute many instructions with the same arguments.

    The result is translated to a form that is can handle all the
     return types used by instructions.

    Does not handle implementation errors (since these can be handled uniformly
     by the user of this class).

    "Controlled" means that implementation errors are not handled - i.e., it only handles flow
    that can be considered "controlled".
    """

    def apply(self, instruction: Instruction) -> PartialInstructionControlledFailureInfo:
        """
        :return: None if the execution was successful.
        """
        raise NotImplementedError()


class SingleInstructionExecutionFailure(tuple):
    """
    Information about a failure of the execution of a single instruction.
    """

    def __new__(cls,
                status: PartialResultStatus,
                source_line: line_source.Line,
                failure_details: FailureDetails):
        return tuple.__new__(cls, (status,
                                   source_line,
                                   failure_details))

    @property
    def status(self) -> PartialResultStatus:
        """
        :return: Never PartialResultStatus.PASS
        """
        return self[0]

    @property
    def source_line(self) -> line_source.Line:
        return self[1]

    @property
    def failure_details(self) -> FailureDetails:
        return self[2]


def execute_element(executor: ControlledInstructionExecutor,
                    element: PhaseContentElement) -> SingleInstructionExecutionFailure:
    """
    :param element: Must be an instruction (i.e., element.is_instruction is True)
    :return: If None, then the execution was successful.
    """

    try:
        fail_info = executor.apply(element.instruction)
        if fail_info is None:
            return None
        return SingleInstructionExecutionFailure(PartialResultStatus(fail_info.status.value),
                                                 element.first_line,
                                                 result.new_failure_details_from_message(fail_info.error_message))
    except Exception as ex:
        return SingleInstructionExecutionFailure(PartialResultStatus.IMPLEMENTATION_ERROR,
                                                 element.first_line,
                                                 result.new_failure_details_from_exception(ex))
