from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic

from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.symbol.sdv_validation import SdvValidator, ConstantSuccessSdvValidator
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep

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


class InstructionEmbryoParserFromTokensWoFileSystemLocationInfo(Generic[T], InstructionEmbryoParser[T], ABC):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> InstructionEmbryo[T]:
        return self._parse(source)

    def _parse(self, source: ParseSource) -> InstructionEmbryo[T]:
        with token_stream_parser.from_parse_source(source,
                                                   consume_last_line_if_is_at_eol_after_parse=True) as token_parser:
            return self._parse_from_tokens(token_parser)

    @abstractmethod
    def _parse_from_tokens(self, token_parser: TokenParser) -> InstructionEmbryo[T]:
        pass
