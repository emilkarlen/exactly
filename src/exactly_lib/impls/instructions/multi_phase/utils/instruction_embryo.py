from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic, Optional

from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_element_parsing import LocationAwareParser
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator, ConstantSuccessSdvValidator

T = TypeVar('T')
RET = TypeVar('RET')


class MainMethodVisitor(Generic[T, RET], ABC):
    @abstractmethod
    def visit_phase_agnostic(self, main_method: 'PhaseAgnosticMainMethod[T]') -> RET:
        pass

    @abstractmethod
    def visit_setup_phase_aware(self, main_method: 'SetupPhaseAwareMainMethod[T]') -> RET:
        pass


class MainMethod(Generic[T], ABC):
    @abstractmethod
    def accept(self, visitor: MainMethodVisitor[T, RET]) -> RET:
        pass


class PhaseAgnosticMainMethod(Generic[T], MainMethod[T], ABC):
    @abstractmethod
    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             ) -> T:
        pass

    def accept(self, visitor: MainMethodVisitor[T, RET]) -> RET:
        return visitor.visit_phase_agnostic(self)


class SetupPhaseAwareMainMethod(Generic[T], MainMethod[T], ABC):
    @abstractmethod
    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             setup_phase_settings: Optional[SetupSettingsBuilder],
             os_services: OsServices,
             ) -> T:
        pass

    def accept(self, visitor: MainMethodVisitor[T, RET]) -> RET:
        return visitor.visit_setup_phase_aware(self)


class MainStepMethodEmbryo(Generic[T], ABC):
    """
    Executor with standard arguments, but custom return type.
    
    The custom return type makes testing easier, by providing access to
    custom result.
    """

    @abstractmethod
    def main_method(self) -> MainMethod[T]:
        pass


class InstructionEmbryo(Generic[T], MainStepMethodEmbryo[T], ABC):
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


class PhaseAgnosticInstructionEmbryo(Generic[T], InstructionEmbryo[T], ABC):
    @abstractmethod
    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             ) -> T:
        pass

    def main_method(self) -> MainMethod[T]:
        return _MainMethodOfPhaseAgnosticInstructionEmbryo(self)


class SetupPhaseAwareInstructionEmbryo(Generic[T], InstructionEmbryo[T], ABC):
    @abstractmethod
    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             setup_phase_settings: Optional[SetupSettingsBuilder],
             os_services: OsServices,
             ) -> T:
        pass

    def main_method(self) -> MainMethod[T]:
        return _MainMethodOfSetupPhaseAwareInstructionEmbryo(self)


class _MainMethodOfPhaseAgnosticInstructionEmbryo(Generic[T], PhaseAgnosticMainMethod[T]):
    def __init__(self, embryo: PhaseAgnosticInstructionEmbryo[T]):
        self._embryo = embryo

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices) -> T:
        return self._embryo.main(environment, settings, os_services)


class _MainMethodOfSetupPhaseAwareInstructionEmbryo(Generic[T], SetupPhaseAwareMainMethod[T]):
    def __init__(self, embryo: SetupPhaseAwareInstructionEmbryo[T]):
        self._embryo = embryo

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             setup_phase_settings: Optional[SetupSettingsBuilder],
             os_services: OsServices) -> T:
        return self._embryo.main(environment, settings, setup_phase_settings, os_services)


class InstructionEmbryoParser(Generic[T], LocationAwareParser[InstructionEmbryo[T]], ABC):
    @abstractmethod
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> InstructionEmbryo[T]:
        pass


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
