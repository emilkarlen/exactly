from abc import ABC, abstractmethod

from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case.actor import AtcOsProcessExecutor
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.file_utils.std import StdFiles
from . import parts


class OsProcessExecutor(parts.Executor, ABC):
    def __init__(self,
                 os_services: OsServices,
                 os_process_executor: AtcOsProcessExecutor,
                 ):
        self.os_services = os_services
        self.os_process_executor = os_process_executor

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                std_files: StdFiles,
                ) -> int:
        command_sdv = self._command_to_execute(environment)
        command = (
            command_sdv
                .resolve(environment.symbols)
                .value_of_any_dependency(environment.tcds)
        )
        return self.os_process_executor.execute(command, std_files, environment.proc_exe_settings)

    @abstractmethod
    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> CommandSdv:
        """
        Called after prepare, to get the command to execute
        """
        pass
