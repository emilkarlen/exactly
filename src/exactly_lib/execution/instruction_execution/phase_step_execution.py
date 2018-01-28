from exactly_lib.execution.instruction_execution.single_instruction_executor import ControlledInstructionExecutor, \
    execute_element
from exactly_lib.execution.phase_step_identifiers.phase_step import PhaseStep
from exactly_lib.execution.result import PartialResult, InstructionFailureInfo, new_partial_result_pass, \
    PartialResultStatus
from exactly_lib.section_document.model import SectionContents, SectionContentElement, ElementType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util import line_source
from exactly_lib.util.failure_details import FailureDetails
from exactly_lib.util.line_source import SourceLocationPath


class ElementHeaderExecutor:
    def apply(self, line: line_source.LineSequence):
        raise NotImplementedError()


class ElementHeaderExecutorThatDoesNothing(ElementHeaderExecutor):
    def apply(self, line: line_source.LineSequence):
        pass


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
                  sds: SandboxDirectoryStructure) -> PartialResult:
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
        return new_partial_result_pass(sds)
    else:
        return PartialResult(
            failure.status,
            sds,
            InstructionFailureInfo(phase_step,
                                   failure.source_location,
                                   failure.failure_details,
                                   failure.element_description)
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
