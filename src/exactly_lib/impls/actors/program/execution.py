import pathlib
from abc import ABC, abstractmethod
from typing import Optional, Sequence

from exactly_lib.impls.actors.util import std_files
from exactly_lib.impls.types.string_source.factory import RootStringSourceFactory
from exactly_lib.impls.types.string_transformer import sequence_resolving
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.type_val_prims.string_source.impls import concat as ss_concat
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.file_utils.std import StdFiles, StdOutputFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from ..util.actor_from_parts import parts


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
                settings: ProcessExecutionSettings,
                stdin: Optional[StringSource],
                output: StdOutputFiles,
                ) -> int:
        program = self._resolve_program(environment, settings)
        stdin_string_source = self._resolve_stdin(stdin,
                                                  program.stdin,
                                                  environment.mem_buff_size)
        with std_files.of_optional_stdin(stdin_string_source, output) as std_files_:
            executor = self._resolve_execution_variant(
                self._app_env(environment, settings),
                program,
                std_files_,
            )
            return executor.execute()

    @staticmethod
    def _resolve_stdin(act_stdin: Optional[StringSource],
                       program_stdin: Sequence[StringSource],
                       mem_buff_size: int,
                       ) -> Optional[StringSource]:
        stdin_parts = list(program_stdin)

        if act_stdin:
            stdin_parts.append(act_stdin)

        return ss_concat.string_source_of_mb_empty_sequence(stdin_parts, mem_buff_size)

    @staticmethod
    def _resolve_execution_variant(app_env: ApplicationEnvironment,
                                   program: Program,
                                   files: StdFiles,
                                   ) -> _ProgramExecutor:
        transformation = sequence_resolving.resolve(program.transformation)
        return (
            _ExecutorWithoutTransformation(app_env, program.command, files)
            if transformation.is_identity_transformer
            else
            _ExecutorWithTransformation(app_env, program, transformation, files)
        )

    def _resolve_program(self,
                         environment: InstructionEnvironmentForPostSdsStep,
                         settings: ProcessExecutionSettings,
                         ) -> Program:
        return (
            self._program.resolve(environment.symbols)
                .value_of_any_dependency(environment.tcds)
                .primitive(self._app_env(environment, settings))
        )

    def _app_env(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 settings: ProcessExecutionSettings,
                 ) -> ApplicationEnvironment:
        return ApplicationEnvironment(
            self._os_services,
            settings,
            environment.tmp_dir__path_access.paths_access,
            environment.mem_buff_size,
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
                 program: Program,
                 resolved_transformer_for_program: StringTransformer,
                 atc_files: StdFiles,
                 ):
        self._app_env = app_env
        self._program = program
        self._resolved_transformer_for_program = resolved_transformer_for_program
        self._atc_files = atc_files
        self._string_source_factory = RootStringSourceFactory(app_env.tmp_files_space)

    def execute(self) -> int:
        untransformed_stdout_path = self._app_env.tmp_files_space.new_path('un-trans-out')

        exit_code_from_command = self._execute_command_w_stdout_to_file(untransformed_stdout_path)

        transformer_input = self._string_source_factory.of_file__poorly_described(untransformed_stdout_path)
        transformer_output = self._resolved_transformer_for_program.transform(transformer_input)

        transformer_output.contents().write_to(self._atc_files.output.out)

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
                self._program.command,
                self._app_env.process_execution_settings,
                command_files,
            )
