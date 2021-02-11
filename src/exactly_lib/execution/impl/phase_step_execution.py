from typing import Optional, TypeVar, Callable

from exactly_lib.execution.failure_info import InstructionFailureInfo, ActPhaseFailureInfo
from exactly_lib.execution.impl.result import Failure
from exactly_lib.execution.impl.single_instruction_executor import ControlledInstructionExecutor, \
    execute_element
from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.execution.result import PhaseStepFailure, ExecutionFailureStatus, PhaseStepFailureException
from exactly_lib.section_document.model import SectionContents, SectionContentElement, ElementType
from exactly_lib.test_case.hard_error import HardErrorException
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
    Exceptions raised by this object are translated to INTERNAL_ERROR.
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
    Exceptions raised by this object are translated to INTERNAL_ERROR.
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
    def __init__(self,
                 step: PhaseStep,
                 actor_name: str,
                 phase_source: str,
                 ):
        self._step = step
        self._actor_name = actor_name
        self._phase_source = phase_source

    def apply(self,
              status: ExecutionFailureStatus,
              failure_details: FailureDetails) -> PhaseStepFailure:
        return PhaseStepFailure(status,
                                ActPhaseFailureInfo(self._step,
                                                    failure_details,
                                                    self._actor_name,
                                                    self._phase_source))

    def hard_error(self, ex: HardErrorException) -> PhaseStepFailure:
        return self.apply(ExecutionFailureStatus.HARD_ERROR,
                          FailureDetails.new_message(ex.error))

    def internal_error(self, ex: Exception, message: Optional[str] = None) -> PhaseStepFailure:
        return self.apply(ExecutionFailureStatus.INTERNAL_ERROR,
                          FailureDetails.new_exception(ex, message))

    def internal_error_msg(self, msg: str) -> PhaseStepFailure:
        return self.apply(ExecutionFailureStatus.INTERNAL_ERROR,
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


def execute_action_and_catch_internal_error_exception(
        action_that_raises_phase_step_or_hard_error_exception: Callable[[], T],
        failure_con: PhaseStepFailureResultConstructor
) -> T:
    """
    :raises PhaseStepFailureException
    """
    # return action_that_raises_phase_step_or_hard_error_exception()  # DEBUG IMPLEMENTATION EXCEPTION
    try:
        return action_that_raises_phase_step_or_hard_error_exception()
    except PhaseStepFailureException:
        raise
    except HardErrorException as ex:
        raise PhaseStepFailureException(failure_con.hard_error(ex))
    except Exception as ex:
        from exactly_lib.util import line_source, traceback_
        raise PhaseStepFailureException(failure_con.internal_error(ex, traceback_.traceback_as_str()))
