from abc import ABC, abstractmethod
from typing import Optional

from exactly_lib.impls.actors.util import std_files
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from . import parts


class OsProcessExecutor(parts.Executor, ABC):
    def __init__(self,
                 os_services: OsServices,
                 ):
        self.os_services = os_services

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                settings: ProcessExecutionSettings,
                stdin: Optional[StringSource],
                output: StdOutputFiles,
                ) -> int:
        command_sdv = self._command_to_execute(environment)
        command = (
            command_sdv
                .resolve(environment.symbols)
                .value_of_any_dependency(environment.tcds)
        )
        with std_files.of_optional_stdin(stdin, output) as std_files_:
            return self.os_services.command_executor.execute(
                command,
                settings,
                std_files_,
            )

    @abstractmethod
    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> CommandSdv:
        """
        Called after prepare, to get the command to execute
        """
        pass
