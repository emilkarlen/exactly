import pathlib

from exactly_lib.act_phase_setups import utils
from exactly_lib.test_case.act_phase_handling import ExitCodeOrHardError
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.process_execution.process_execution_settings import Command
from exactly_lib.util.std import StdFiles
from . import parts


class CommandExecutor(parts.Executor):
    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return utils.execute_sub_process(self._command_to_execute(environment, script_output_dir_path),
                                         std_files,
                                         environment.process_execution_settings)

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            script_output_dir_path: pathlib.Path) -> Command:
        """
        Called after prepare, to get the command to execute
        """
        raise NotImplementedError()
