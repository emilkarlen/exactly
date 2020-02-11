import pathlib

from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case.actor import AtcOsProcessExecutor
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.util.std import StdFiles
from . import parts


class SubProcessExecutor(parts.Executor):
    def __init__(self, os_process_executor: AtcOsProcessExecutor):
        self.os_process_executor = os_process_executor

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        command_sdv = self._command_to_execute(script_output_dir_path)
        command = (
            command_sdv
                .resolve(environment.symbols)
                .value_of_any_dependency(environment.tcds)
        )
        return self.os_process_executor.execute(command,
                                                std_files,
                                                environment.process_execution_settings)

    def _command_to_execute(self, script_output_dir_path: pathlib.Path) -> CommandSdv:
        """
        Called after prepare, to get the command to execute
        """
        raise NotImplementedError('abstract method')


class CommandResolverExecutor(SubProcessExecutor):
    def __init__(self,
                 os_process_executor: AtcOsProcessExecutor,
                 command_sdv: CommandSdv):
        super().__init__(os_process_executor)
        self.command_sdv = command_sdv

    def _command_to_execute(self, script_output_dir_path: pathlib.Path) -> CommandSdv:
        return self.command_sdv
