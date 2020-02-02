from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case.validation.sdv_validation import SdvValidator, ConstantSuccessSdvValidator

T = TypeVar('T')


class MainStepExecutorEmbryo(Generic[T], ABC):
    """
    Executor with standard arguments, but custom return type.
    
    The custom return type makes testing easier, by providing access to
    custom result.
    """

    @abstractmethod
    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices,
             ) -> T:
        pass


class InstructionEmbryo(Generic[T], MainStepExecutorEmbryo[T], ABC):
    """
    Instruction embryo that makes it easy to both
    test using custom information (in sub classes),
    and integrate into many phases.
    
    A multi-phase instruction may sub class this class,
    to achieve both easy testing (by giving access to things that
    are specific for the instruction in question),
    and integrate into different phases.
    """

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return []

    @property
    def validator(self) -> SdvValidator:
        return ConstantSuccessSdvValidator()


class InstructionEmbryoParser(Generic[T]):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> InstructionEmbryo[T]:
        raise NotImplementedError()


class InstructionEmbryoParserWoFileSystemLocationInfo(Generic[T], InstructionEmbryoParser[T]):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> InstructionEmbryo[T]:
        return self._parse(source)

    def _parse(self, source: ParseSource) -> InstructionEmbryo[T]:
        raise NotImplementedError('abstract method')


class InstructionEmbryoParserThatConsumesCurrentLine(Generic[T], InstructionEmbryoParser[T]):
    """
    A parser that unconditionally consumes the current line,
    and that uses the remaining part of the current line for
    constructing the parsed instruction.

    The parser cannot consume any more than the current line.

    Precondition: The source must have a current line.
    """

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> InstructionEmbryo[T]:
        rest_of_line = source.remaining_part_of_current_line
        source.consume_current_line()
        return self._parse(rest_of_line)

    def _parse(self, rest_of_line: str) -> InstructionEmbryo[T]:
        raise NotImplementedError()
