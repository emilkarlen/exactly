from abc import ABC, abstractmethod

from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case.actor import AtcOsProcessExecutor
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.util.file_utils.std import StdFiles
from . import parts


class OsProcessExecutor(parts.Executor, ABC):
    def __init__(self, os_process_executor: AtcOsProcessExecutor):
        self.os_process_executor = os_process_executor

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                std_files: StdFiles,
                ) -> ExitCodeOrHardError:
        command_sdv = self._command_to_execute(environment)
        command = (
            command_sdv
                .resolve(environment.symbols)
                .value_of_any_dependency(environment.tcds)
        )
        return self.os_process_executor.execute(command,
                                                std_files,
                                                environment.proc_exe_settings)

    @abstractmethod
    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> CommandSdv:
        """
        Called after prepare, to get the command to execute
        """
        pass


class CommandResolverExecutor(OsProcessExecutor):
    def __init__(self,
                 os_process_executor: AtcOsProcessExecutor,
                 command_sdv: CommandSdv,
                 ):
        super().__init__(os_process_executor)
        self.command_sdv = command_sdv

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> CommandSdv:
        return self.command_sdv
