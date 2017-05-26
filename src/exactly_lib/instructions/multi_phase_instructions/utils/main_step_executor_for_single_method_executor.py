"""
Utilities to help constructing an instruction for a specific phase, from phase-independent parts.
"""

from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import MainStepExecutor
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh


class MainStepExecutorForGenericMethodWithStringErrorMessage(MainStepExecutor):
    """
    A `MainStepExecutor` implemented by a single method that.
    """

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                logging_paths: PhaseLoggingPaths,
                os_services: OsServices) -> str:
        """
        :return: None if successful, otherwise an error message as a string
        """
        raise NotImplementedError()

    def apply_as_non_assertion(self,
                               environment: InstructionEnvironmentForPostSdsStep,
                               logging_paths: PhaseLoggingPaths,
                               os_services: OsServices) -> sh.SuccessOrHardError:
        error_message = self.execute(environment, logging_paths, os_services)
        return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)

    def apply_as_assertion(self,
                           environment: InstructionEnvironmentForPostSdsStep,
                           logging_paths: PhaseLoggingPaths,
                           os_services: OsServices) -> pfh.PassOrFailOrHardError:
        error_message = self.execute(environment, logging_paths, os_services)
        return pfh.new_pfh_pass() if error_message is None else pfh.new_pfh_hard_error(error_message)
