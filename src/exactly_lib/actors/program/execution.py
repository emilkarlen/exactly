from abc import ABC

from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.file_utils.std import StdFiles
from ..util.actor_from_parts import parts
from ...symbol.logic.program.program_sdv import ProgramSdv
from ...test_case.os_services import OsServices
from ...type_system.logic.application_environment import ApplicationEnvironment
from ...type_system.logic.program.process_execution.command import Command


class Executor(parts.Executor, ABC):
    def __init__(self,
                 os_services: OsServices,
                 program: ProgramSdv,
                 ):
        self._os_services = os_services
        self._program = program

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                std_files: StdFiles,
                ) -> int:
        return self._os_services.command_executor.execute(
            self._command_to_execute(environment),
            environment.proc_exe_settings,
            std_files,
        )

    def _command_to_execute(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> Command:
        return (
            self._program.resolve(environment.symbols)
                .value_of_any_dependency(environment.tcds)
                .primitive(self._app_env(environment))
                .command
        )

    def _app_env(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 ) -> ApplicationEnvironment:
        return ApplicationEnvironment(
            self._os_services,
            environment.proc_exe_settings,
            environment.tmp_dir__path_access.paths_access,
        )
