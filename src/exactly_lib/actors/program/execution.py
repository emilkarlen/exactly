import pathlib
from abc import ABC, abstractmethod

from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.file_utils.std import StdFiles, StdOutputFiles
from ..util.actor_from_parts import parts
from ...symbol.logic.program.program_sdv import ProgramSdv
from ...test_case.os_services import OsServices
from ...test_case_utils.string_models.factory import RootStringModelFactory
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
                 atc_files: StdFiles,
                 ):
        self._app_env = app_env
        self._command = command
        self._atc_files = atc_files

    def execute(self) -> int:
        return self._app_env.os_services.command_executor.execute(
            self._command,
            self._app_env.process_execution_settings,
            self._atc_files,
        )


class _ExecutorWithTransformation(_ProgramExecutor):
    def __init__(self,
                 app_env: ApplicationEnvironment,
                 program_w_trans: Program,
                 atc_files: StdFiles,
                 ):
        self._app_env = app_env
        self._program_w_trans = program_w_trans
        self._atc_files = atc_files
        self._string_model_factory = RootStringModelFactory(app_env.tmp_files_space)

    def execute(self) -> int:
        untransformed_stdout_path = self._app_env.tmp_files_space.new_path('un-trans-out')

        exit_code_from_command = self._execute_command_w_stdout_to_file(untransformed_stdout_path)

        transformer_input = self._string_model_factory.of_file(untransformed_stdout_path)
        transformer_output = self._program_w_trans.transformation.transform(transformer_input)

        transformer_output.write_to(self._atc_files.output.out)

        return exit_code_from_command

    def _execute_command_w_stdout_to_file(self, stdout_path: pathlib.Path) -> int:
        with stdout_path.open('w') as stdout_file:
            command_files = StdFiles(
                self._atc_files.stdin,
                StdOutputFiles(
                    stdout_file=stdout_file,
                    stderr_file=self._atc_files.output.err,
                )
            )
            return self._app_env.os_services.command_executor.execute(
                self._program_w_trans.command,
                self._app_env.process_execution_settings,
                command_files,
            )
