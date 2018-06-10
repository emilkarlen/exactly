import pathlib

from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.util.std import StdFiles
from . import parts


class SubProcessExecutor(parts.Executor):
    def __init__(self, os_process_executor: ActPhaseOsProcessExecutor):
        self.os_process_executor = os_process_executor

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        command_resolver = self._command_to_execute(script_output_dir_path)
        command = command_resolver.resolve_of_any_dep(environment.path_resolving_environment_pre_or_post_sds)
        return self.os_process_executor.execute(command,
                                                std_files,
                                                environment.process_execution_settings)

    def _command_to_execute(self, script_output_dir_path: pathlib.Path) -> CommandResolver:
        """
        Called after prepare, to get the command to execute
        """
        raise NotImplementedError('abstract method')


class CommandResolverExecutor(SubProcessExecutor):
    def __init__(self,
                 os_process_executor: ActPhaseOsProcessExecutor,
                 command_resolver: CommandResolver):
        super().__init__(os_process_executor)
        self.command_resolver = command_resolver

    def _command_to_execute(self, script_output_dir_path: pathlib.Path) -> CommandResolver:
        return self.command_resolver
