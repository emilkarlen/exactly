from typing import Optional, TypeVar, Callable

from exactly_lib.execution.failure_info import InstructionFailureInfo, PhaseFailureInfo
from exactly_lib.execution.impl.result import Failure
from exactly_lib.execution.impl.single_instruction_executor import ControlledInstructionExecutor, \
    execute_element
from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.execution.result import PhaseStepFailure, ExecutionFailureStatus, PhaseStepFailureException
from exactly_lib.section_document.model import SectionContents, SectionContentElement, ElementType
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util import line_source


class ElementHeaderExecutor:
    def apply(self, line: line_source.LineSequence):
        raise NotImplementedError()


class ElementHeaderExecutorThatDoesNothing(ElementHeaderExecutor):
    def apply(self, line: line_source.LineSequence):
        pass


def execute_phase(phase_contents: SectionContents,
                  header_executor_for_comment: ElementHeaderExecutor,
                  header_executor_for_instruction: ElementHeaderExecutor,
                  instruction_executor: ControlledInstructionExecutor,
                  phase_step: PhaseStep) -> Optional[PhaseStepFailure]:
    """
    Executes the elements of a given phase/step.
    Catches exceptions thrown by instruction-execution and "reports" them as
    internal errors.
    Stops execution at the first failing instruction.

    :param phase_contents:
    :param header_executor_for_comment: Is executed for each element that is a comment.
    Exceptions raised by this object are not handled.
    :param header_executor_for_instruction: Is executed for each element that is an instruction
    Exceptions raised by this object are not handled.
    :param instruction_executor: Is executed for each element that is an instruction, after
    header_executor_for_instruction has been executed.
    Exceptions raised by this object are translated to IMPLEMENTATION_ERROR.
    :return: None, if there was no error. Otherwise, the first error.
    """
    failure = execute_phase_prim(phase_contents,
                                 header_executor_for_comment,
                                 header_executor_for_instruction,
                                 instruction_executor)
    if failure is None:
        return None
    else:
        return PhaseStepFailure(
            failure.status,
            InstructionFailureInfo(phase_step,
                                   failure.source_location,
                                   failure.failure_details,
                                   failure.element_description)
        )


def execute_phase_prim(phase_contents: SectionContents,
                       header_executor_for_comment: ElementHeaderExecutor,
                       header_executor_for_instruction: ElementHeaderExecutor,
                       instruction_executor: ControlledInstructionExecutor) -> Optional[Failure]:
    """
    Executes the elements of a given phase/step.
    Catches exceptions thrown by instruction-execution and "reports" them as
    internal errors.
    Stops execution at the first failing instruction.

    :param phase_contents:
    :param header_executor_for_comment: Is executed for each element that is a comment.
    Exceptions raised by this object are not handled.
    :param header_executor_for_instruction: Is executed for each element that is an instruction
    Exceptions raised by this object are not handled.
    :param instruction_executor: Is executed for each element that is an instruction, after
    header_executor_for_instruction has been executed.
    Exceptions raised by this object are translated to IMPLEMENTATION_ERROR.
    :return: None, if there was no error. Otherwise, the first error.
    """
    for element in phase_contents.elements:
        assert isinstance(element, SectionContentElement)
        if element.element_type is ElementType.COMMENT:
            header_executor_for_comment.apply(element.source)
        elif element.element_type is ElementType.INSTRUCTION:
            header_executor_for_instruction.apply(element.source)
            instruction_info = element.instruction_info
            failure_info = execute_element(instruction_executor,
                                           element,
                                           instruction_info)
            if failure_info is not None:
                return Failure(failure_info.status,
                               failure_info.source_location_path,
                               failure_info.failure_details,
                               instruction_info.description)
    return None


class PhaseStepFailureResultConstructor:
    def __init__(self, step: PhaseStep):
        self.step = step

    def apply(self,
              status: ExecutionFailureStatus,
              failure_details: FailureDetails) -> PhaseStepFailure:
        return PhaseStepFailure(status,
                                PhaseFailureInfo(self.step,
                                                 failure_details))

    def implementation_error(self, ex: Exception) -> PhaseStepFailure:
        return self.apply(ExecutionFailureStatus.IMPLEMENTATION_ERROR,
                          FailureDetails.new_exception(ex))

    def implementation_error_msg(self, msg: str) -> PhaseStepFailure:
        return self.apply(ExecutionFailureStatus.IMPLEMENTATION_ERROR,
                          FailureDetails.new_constant_message(msg))


def run_instructions_phase_step(step: PhaseStep,
                                instruction_executor: ControlledInstructionExecutor,
                                phase_contents: SectionContents):
    """
    :raises PhaseStepFailureException
    """
    res = execute_phase(phase_contents,
                        ElementHeaderExecutorThatDoesNothing(),
                        ElementHeaderExecutorThatDoesNothing(),
                        instruction_executor,
                        step)
    if res is not None:
        raise PhaseStepFailureException(res)


T = TypeVar('T')


def execute_action_and_catch_implementation_exception(action_that_raises_phase_step_failure_exception: Callable[[], T],
                                                      failure_con: PhaseStepFailureResultConstructor
                                                      ) -> T:
    """
    :raises PhaseStepFailureException
    """
    # return action_that_raises_phase_step_failure_exception()  # DEBUG IMPLEMENTATION EXCEPTION
    try:
        return action_that_raises_phase_step_failure_exception()
    except PhaseStepFailureException:
        raise
    except Exception as ex:
        raise PhaseStepFailureException(failure_con.implementation_error(ex))
