from exactly_lib.instructions.utils.main_step_executor import MainStepExecutor
from exactly_lib.instructions.utils.sub_process_execution import ResultAndStderr, result_to_sh, result_to_pfh
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh


class MainStepExecutorForSubProcess(MainStepExecutor):
    """
    A MainStepExecutor for executing an external program as a sub process.
    """

    def _apply(self,
               environment: InstructionEnvironmentForPostSdsStep,
               logging_paths: PhaseLoggingPaths,
               os_services: OsServices) -> ResultAndStderr:
        raise NotImplementedError()

    def apply_sh(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 logging_paths: PhaseLoggingPaths,
                 os_services: OsServices) -> sh.SuccessOrHardError:
        return result_to_sh(self._apply(environment, logging_paths, os_services))

    def apply_pfh(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  logging_paths: PhaseLoggingPaths,
                  os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return result_to_pfh(self._apply(environment, logging_paths, os_services))
