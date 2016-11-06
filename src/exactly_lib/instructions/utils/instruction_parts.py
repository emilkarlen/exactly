"""
Utilities to help constructing an instruction for a specific phase, from phase-independent parts.
"""
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsValidator
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
                validator: PreOrPostEdsValidator,
                executor: MainStepExecutor):
        return tuple.__new__(cls, (validator, executor))

    @property
    def validator(self) -> PreOrPostEdsValidator:
        return self[0]

    @property
    def executor(self) -> MainStepExecutor:
        return self[1]
