from enum import Enum
from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.execution.result import ExecutionFailureStatus
from exactly_lib.section_document.model import SectionContentElement, InstructionInfo
from exactly_lib.section_document.source_location import SourceLocationPath
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.result import failure_details
from exactly_lib.test_case.result.failure_details import FailureDetails


class PartialControlledFailureEnum(Enum):
    """
    Implementation notes: integer values must correspond to PartialExeResultStatus

    "controlled" means that implementation errors are not handled.
    """
    VALIDATION_ERROR = 1
    FAIL = 2
    HARD_ERROR = 99


class PartialInstructionControlledFailureInfo(tuple):
    """
    "controlled" means that implementation errors are not handled.
    """

    def __new__(cls,
                status: PartialControlledFailureEnum,
                error_message: TextRenderer):
        return tuple.__new__(cls, (status,
                                   error_message))

    @property
    def status(self) -> PartialControlledFailureEnum:
        return self[0]

    @property
    def error_message(self) -> TextRenderer:
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

    def apply(self, instruction: TestCaseInstruction) -> PartialInstructionControlledFailureInfo:
        """
        :return: None if the execution was successful.
        """
        raise NotImplementedError()


class SingleInstructionExecutionFailure(tuple):
    """
    Information about a failure of the execution of a single instruction.
    """

    def __new__(cls,
                status: ExecutionFailureStatus,
                source_location: SourceLocationPath,
                details: failure_details.FailureDetails):
        return tuple.__new__(cls, (status,
                                   source_location,
                                   details))

    @property
    def status(self) -> ExecutionFailureStatus:
        """
        :return: Never PartialExeResultStatus.PASS
        """
        return self[0]

    @property
    def source_location_path(self) -> SourceLocationPath:
        return self[1]

    @property
    def failure_details(self) -> failure_details.FailureDetails:
        return self[2]


def execute_element(executor: ControlledInstructionExecutor,
                    element: SectionContentElement,
                    instruction_info: InstructionInfo) -> Optional[SingleInstructionExecutionFailure]:
    """
    :param element: Must be an instruction (i.e., element.is_instruction is True)
    :return: If None, then the execution was successful.
    """

    try:
        instruction = instruction_info.instruction
        assert isinstance(instruction, TestCaseInstruction), _INSTRUCTION_TYPE_ERROR_MESSAGE
        fail_info = executor.apply(instruction)
        if fail_info is None:
            return None
        return SingleInstructionExecutionFailure(
            ExecutionFailureStatus(fail_info.status.value),
            element.source_location_info.source_location_path,
            FailureDetails.new_message(fail_info.error_message))
    except HardErrorException as ex:
        return SingleInstructionExecutionFailure(
            ExecutionFailureStatus.HARD_ERROR,
            element.source_location_info.source_location_path,
            FailureDetails.new_message(ex.error)
        )
    except Exception as ex:
        from exactly_lib.util import traceback_
        return SingleInstructionExecutionFailure(
            ExecutionFailureStatus.INTERNAL_ERROR,
            element.source_location_info.source_location_path,
            FailureDetails.new_exception(ex, traceback_.traceback_as_str())
        )


_INSTRUCTION_TYPE_ERROR_MESSAGE = 'Instruction in test-case must be ' + str(TestCaseInstruction)
