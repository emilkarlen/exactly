from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.section_document.source_location import SourceLocationPath
from exactly_lib.test_case.result.failure_details import FailureDetails

RET = TypeVar('RET')


class FailureInfoVisitor(Generic[RET], ABC):
    @abstractmethod
    def visit_instruction_failure(self, failure_info: 'InstructionFailureInfo') -> RET:
        pass

    @abstractmethod
    def visit_phase_failure(self, failure_info: 'PhaseFailureInfo') -> RET:
        pass


class FailureInfo(ABC):
    def __init__(self,
                 phase_step: PhaseStep,
                 failure_details: FailureDetails,
                 ):
        self.__phase_step = phase_step
        self.__failure_details = failure_details

    @property
    def phase_step(self) -> PhaseStep:
        return self.__phase_step

    @property
    def failure_details(self) -> FailureDetails:
        return self.__failure_details

    @property
    @abstractmethod
    def source_location(self) -> Optional[SourceLocationPath]:
        pass

    @abstractmethod
    def accept(self, visitor: FailureInfoVisitor[RET]) -> RET:
        pass

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
                 element_description: str = None,
                 ):
        super().__init__(phase_step, failure_details)
        self.__source_location = source_location
        self.__phase_step = phase_step
        self.__element_description = element_description

    @property
    def source_location(self) -> SourceLocationPath:
        return self.__source_location

    @property
    def element_description(self) -> str:
        return self.__element_description

    def accept(self, visitor: FailureInfoVisitor[RET]) -> RET:
        return visitor.visit_instruction_failure(self)


class PhaseFailureInfo(FailureInfo):
    def __init__(self,
                 phase_step: PhaseStep,
                 failure_details: FailureDetails,
                 phase_source: Optional[str] = None,
                 ):
        super().__init__(phase_step, failure_details)
        self._phase_source = phase_source

    @property
    def source_location(self) -> Optional[SourceLocationPath]:
        return None

    @property
    def phase_source(self) -> Optional[str]:
        return self._phase_source

    def accept(self, visitor: FailureInfoVisitor[RET]) -> RET:
        return visitor.visit_phase_failure(self)
