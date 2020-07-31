from abc import ABC, abstractmethod

from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.file_utils.std import StdFiles
from ..util.actor_from_parts import parts
from ...symbol.logic.program.program_sdv import ProgramSdv
from ...test_case.os_services import OsServices
from ...type_system.logic.application_environment import ApplicationEnvironment
from ...type_system.logic.program.process_execution.command import Command
from ...type_system.logic.program.program import Program


class _ProgramExecutor(ABC):
    @abstractmethod
    def execute(self) -> int:
        pass


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
        executor = self._resolve_execution_variant(
            self._app_env(environment),
            self._resolve_program(environment),
            std_files,
        )
        return executor.execute()

    @staticmethod
    def _resolve_execution_variant(app_env: ApplicationEnvironment,
                                   program: Program,
                                   files: StdFiles,
                                   ) -> _ProgramExecutor:
        return (
            _ExecutorWithoutTransformation(app_env, program.command, files)
            if program.transformation.is_identity_transformer
            else
            _ExecutorWithTransformation(app_env, program, files)
        )

    def _resolve_program(self,
                         environment: InstructionEnvironmentForPostSdsStep,
                         ) -> Program:
        return (
            self._program.resolve(environment.symbols)
                .value_of_any_dependency(environment.tcds)
                .primitive(self._app_env(environment))
        )

    def _app_env(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 ) -> ApplicationEnvironment:
        return ApplicationEnvironment(
            self._os_services,
            environment.proc_exe_settings,
            environment.tmp_dir__path_access.paths_access,
        )


class _ExecutorWithoutTransformation(_ProgramExecutor):
    def __init__(self,
                 app_env: ApplicationEnvironment,
                 command: Command,
                 files: StdFiles,
                 ):
        self._app_env = app_env
        self._command = command
        self._files = files

    def execute(self) -> int:
        return self._app_env.os_services.command_executor.execute(
            self._command,
            self._app_env.process_execution_settings,
            self._files,
        )


class _ExecutorWithTransformation(_ProgramExecutor):
    def __init__(self,
                 app_env: ApplicationEnvironment,
                 program_w_trans: Program,
                 files: StdFiles,
                 ):
        self._app_env = app_env
        self._program_w_trans = program_w_trans
        self._files = files

    def execute(self) -> int:
        return self._app_env.os_services.command_executor.execute(
            self._program_w_trans.command,
            self._app_env.process_execution_settings,
            self._files,
        )
