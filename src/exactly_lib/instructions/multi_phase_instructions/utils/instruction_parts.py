"""
Utilities to help constructing an instruction for a specific phase, from phase-independent parts.
"""
import types

from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh


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
                validator: PreOrPostSdsValidator,
                executor: MainStepExecutor,
                symbol_usages: tuple = ()):
        return tuple.__new__(cls, (validator, executor, list(symbol_usages)))

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self[0]

    @property
    def executor(self) -> MainStepExecutor:
        return self[1]

    @property
    def symbol_usages(self) -> list:
        return self[2]


class InstructionInfoForConstructingAnInstructionFromParts(tuple):
    """
    The information about an instruction needed to construct an instruction parser
    that constructs an instruction for a specific phase using InstructionParts.

    Each phase can have a utility method that constructs an object of this type
    given just an instruction name.

    This class is an abstraction that is motivated primarily for ease of testing.
    For a specific phase, it makes it possible to vary as little as possible between
    individual instructions, so that it is possible to test as much common code as possible.

    The motivation for this testing is that it is very important that different instructions
    execute sub processes in the same manner (timeout, environment variables, etc).
    """

    def __new__(cls,
                instruction_name: str,
                instruction_parts_2_instruction_function):
        return tuple.__new__(cls, (instruction_name, instruction_parts_2_instruction_function))

    @property
    def instruction_name(self) -> str:
        return self[0]

    @property
    def instruction_parts_2_instruction_function(self) -> types.FunctionType:
        return self[1]


class InstructionPartsParser:
    """
    Parser of `InstructionParts` - used by instructions that may be used in multiple phases. 
    """

    def parse(self, source: ParseSource) -> InstructionParts:
        raise NotImplementedError()
