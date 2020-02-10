"""
Utilities to help constructing an instruction for a specific phase, from phase-independent parts.
"""

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.sdv_validation import SdvValidator
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case.result import pfh, sh


class MainStepExecutor:
    """
    Executes the main step of an instruction in any phase.
    """

    def apply_as_non_assertion(self,
                               environment: InstructionEnvironmentForPostSdsStep,
                               logging_paths: PhaseLoggingPaths,
                               os_services: OsServices) -> sh.SuccessOrHardError:
        """
        Invokes the execution as part of an instruction that is not in the assert phase.
        """
        raise NotImplementedError()

    def apply_as_assertion(self,
                           environment: InstructionEnvironmentForPostSdsStep,
                           logging_paths: PhaseLoggingPaths,
                           os_services: OsServices) -> pfh.PassOrFailOrHardError:
        """
        Invokes the execution as part of an instruction that is in the assert phase.
        """
        raise NotImplementedError()


class InstructionParts(tuple):
    """
    Parts needed for constructing an instruction that uses a MainStepExecutor.

    This class is designed to be used by phase-specific code that constructs
    an instruction for the specific phase,
    given the information in this class.
    """

    def __new__(cls,
                validator: SdvValidator,
                executor: MainStepExecutor,
                symbol_usages: tuple = ()):
        return tuple.__new__(cls, (validator, executor, list(symbol_usages)))

    @property
    def validator(self) -> SdvValidator:
        return self[0]

    @property
    def executor(self) -> MainStepExecutor:
        return self[1]

    @property
    def symbol_usages(self) -> list:
        return self[2]


class InstructionPartsParser:
    """
    Parser of `InstructionParts` - used by instructions that may be used in multiple phases. 
    """

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> InstructionParts:
        raise NotImplementedError()
