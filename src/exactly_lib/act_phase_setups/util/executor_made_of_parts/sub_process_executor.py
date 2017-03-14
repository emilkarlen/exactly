import pathlib

from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.test_case.eh import ExitCodeOrHardError
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.process_execution.os_process_execution import Command
from exactly_lib.util.std import StdFiles
from . import parts


class CommandExecutor(parts.Executor):
    def __init__(self,
                 os_process_executor: ActPhaseOsProcessExecutor):
        self.os_process_executor = os_process_executor

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return self.os_process_executor.execute(self._command_to_execute(environment, script_output_dir_path),
                                                std_files,
                                                environment.process_execution_settings)

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        """
        Called after prepare, to get the command to execute
        """
        raise NotImplementedError()
