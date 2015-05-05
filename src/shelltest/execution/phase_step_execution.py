from shelltest.phase_instr import line_source
from shelltest.execution.single_instruction_executor import ControlledInstructionExecutor, execute_element
from shelltest.phase_instr.model import PhaseContents, PhaseContentElement
from shelltest import phases
from .execution_directory_structure import ExecutionDirectoryStructure
from .result import PartialResult, InstructionFailureInfo, new_partial_result_pass


class ElementHeaderExecutor:
    def apply(self, line: line_source.Line):
        raise NotImplementedError()


class ElementHeaderExecutorThatDoesNothing(ElementHeaderExecutor):
    def apply(self, line: line_source.Line):
        pass


def execute_phase(phase_contents: PhaseContents,
                  header_executor_for_comment: ElementHeaderExecutor,
                  header_executor_for_instruction: ElementHeaderExecutor,
                  instruction_executor: ControlledInstructionExecutor,
                  phase: phases.Phase,
                  phase_step: str,
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
    :param phase:
    :param phase_step:
    :param eds:
    :return: PASS status, if there was no error. Otherwise, the first error.
    """
    for element in phase_contents.elements:
        assert isinstance(element, PhaseContentElement)
        if element.is_comment:
            header_executor_for_comment.apply(element.source_line)
        else:
            header_executor_for_instruction.apply(element.source_line)
            failure_info = execute_element(instruction_executor,
                                           element)
            if failure_info is not None:
                return PartialResult(failure_info.status,
                                     eds,
                                     InstructionFailureInfo(phase,
                                                            phase_step,
                                                            failure_info.source_line,
                                                            failure_info.failure_details))
    return new_partial_result_pass(eds)


