from typing import TypeVar, Generic

from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.section_document.source_location import SourceLocationPath
from exactly_lib.test_case.result.failure_details import FailureDetails


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


RET = TypeVar('RET')


class FailureInfoVisitor(Generic[RET]):
    def visit(self,
              failure_info: FailureInfo) -> RET:
        if isinstance(failure_info, InstructionFailureInfo):
            return self._visit_instruction_failure(failure_info)
        elif isinstance(failure_info, PhaseFailureInfo):
            return self._visit_phase_failure(failure_info)
        else:
            raise TypeError('Unknown FailureInfo: {}'.format(type(failure_info)))

    def _visit_instruction_failure(self,
                                   failure_info: InstructionFailureInfo) -> RET:
        raise NotImplementedError('abstract method')

    def _visit_phase_failure(self,
                             failure_info: PhaseFailureInfo) -> RET:
        raise NotImplementedError('abstract method')
