from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.execution.instruction_execution.single_instruction_executor import ControlledInstructionExecutor, \
    execute_element
from exactly_lib.execution.phase_step_identifiers.phase_step import PhaseStep
from exactly_lib.execution.result import PartialResult, InstructionFailureInfo, new_partial_result_pass, \
    PartialResultStatus
from exactly_lib.section_document.model import SectionContents, SectionContentElement, ElementType
from exactly_lib.util import line_source
from exactly_lib.util.failure_details import FailureDetails


class ElementHeaderExecutor:
    def apply(self, line: line_source.Line):
        raise NotImplementedError()


class ElementHeaderExecutorThatDoesNothing(ElementHeaderExecutor):
    def apply(self, line: line_source.Line):
        pass


class Failure(tuple):
    def __new__(cls,
                status: PartialResultStatus,
                source_line: line_source.Line,
                failure_details: FailureDetails):
        return tuple.__new__(cls, (status, source_line, failure_details))

    @property
    def status(self) -> PartialResultStatus:
        return self[0]

    @property
    def source_line(self) -> line_source.Line:
        return self[1]

    @property
    def failure_details(self) -> FailureDetails:
        return self[2]


def non_instruction_failure(status: PartialResultStatus,
                            failure_details: FailureDetails) -> Failure:
    return Failure(status,
                   None,
                   failure_details)


def execute_phase(phase_contents: SectionContents,
                  header_executor_for_comment: ElementHeaderExecutor,
                  header_executor_for_instruction: ElementHeaderExecutor,
                  instruction_executor: ControlledInstructionExecutor,
                  phase_step: PhaseStep,
                  eds: ExecutionDirectoryStructure) -> PartialResult:
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
    :return: PASS status, if there was no error. Otherwise, the first error.
    """
    failure = execute_phase_prim(phase_contents,
                                 header_executor_for_comment,
                                 header_executor_for_instruction,
                                 instruction_executor)
    if failure is None:
        return new_partial_result_pass(eds)
    else:
        return PartialResult(
                failure.status,
                eds,
                InstructionFailureInfo(phase_step,
                                       failure.source_line,
                                       failure.failure_details)
        )


def execute_phase_prim(phase_contents: SectionContents,
                       header_executor_for_comment: ElementHeaderExecutor,
                       header_executor_for_instruction: ElementHeaderExecutor,
                       instruction_executor: ControlledInstructionExecutor) -> Failure:
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
    :return: PASS status, if there was no error. Otherwise, the first error.
    """
    for element in phase_contents.elements:
        assert isinstance(element, SectionContentElement)
        if element.element_type is ElementType.COMMENT:
            header_executor_for_comment.apply(element.first_line)
        elif element.element_type is ElementType.INSTRUCTION:
            header_executor_for_instruction.apply(element.first_line)
            failure_info = execute_element(instruction_executor,
                                           element)
            if failure_info is not None:
                return Failure(failure_info.status,
                               failure_info.source_line,
                               failure_info.failure_details)
    return None
