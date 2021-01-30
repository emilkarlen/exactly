import pathlib
from typing import ContextManager

from exactly_lib.impls.program_execution.command_processor import CommandProcessor
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.file_utils import ensure_file_existence
from exactly_lib.util.file_utils.std import ProcessExecutionFile, StdFiles, StdOutputFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.process_execution.result_files import ResultFile, DirWithResultFiles


class ExitCodeAndFiles(tuple):
    def __new__(cls,
                exit_code: int,
                files: DirWithResultFiles,
                ):
        return tuple.__new__(cls, (exit_code,
                                   files))

    @property
    def exit_code(self) -> int:
        return self[0]

    @property
    def files(self) -> DirWithResultFiles:
        return self[1]

    @property
    def stderr_file(self) -> pathlib.Path:
        return self[1].path_of_std(ProcOutputFile.STDERR)


class ExitCodeAndStderrFile(tuple):
    def __new__(cls,
                exit_code: int,
                stderr: pathlib.Path,
                ):
        return tuple.__new__(cls, (exit_code,
                                   stderr))

    @property
    def exit_code(self) -> int:
        return self[0]

    @property
    def stderr(self) -> pathlib.Path:
        return self[1]


class ProcessorThatStoresResultInFilesInDir(CommandProcessor[ExitCodeAndFiles]):
    """An object must only be used for a single execution."""

    def __init__(self,
                 executor: CommandExecutor,
                 storage_dir_created_on_demand: pathlib.Path,
                 stdin: ContextManager[ProcessExecutionFile],
                 ):
        """
        :param storage_dir_created_on_demand: Must be a directory that does not contain a file
        with any of the process output file names, or a non-existing path,
        that can be created as a dir.
        """
        self._storage_dir_created_on_demand = DirWithResultFiles(storage_dir_created_on_demand)
        self._executor = executor
        self._stdin = stdin

    @property
    def storage_dir(self) -> DirWithResultFiles:
        return self._storage_dir_created_on_demand

    def process(self,
                settings: ProcessExecutionSettings,
                command: Command,
                ) -> ExitCodeAndFiles:
        """
        :return: Exit code from successful execution
        :raises ExecutionException: Either unable to execute, or execution timed out
        """
        storage_dir = self._storage_dir_created_on_demand
        ensure_file_existence.ensure_directory_exists_as_a_directory__impl_error(storage_dir.directory)
        stdout_path = storage_dir.path_of_result(ResultFile.STD_OUT)
        stderr_path = storage_dir.path_of_result(ResultFile.STD_ERR)
        exit_code_path = storage_dir.path_of_result(ResultFile.EXIT_CODE)

        with self._stdin as f_stdin:
            with stdout_path.open('w') as f_stdout:
                with stderr_path.open('w') as f_stderr:
                    exit_code = self._executor.execute(
                        command,
                        settings,
                        StdFiles(
                            f_stdin,
                            StdOutputFiles(
                                f_stdout,
                                f_stderr,
                            ),
                        ),
                    )
        with exit_code_path.open('w') as exit_code_f:
            exit_code_f.write(str(exit_code))

        return ExitCodeAndFiles(exit_code, storage_dir)


class ProcessorThatStoresStderrInFiles(CommandProcessor[ExitCodeAndStderrFile]):
    """An object must only be used for a single execution."""

    def __init__(self,
                 executor: CommandExecutor,
                 stdin: ContextManager[ProcessExecutionFile],
                 stdout: ContextManager[ProcessExecutionFile],
                 stderr_path_created_on_demand: pathlib.Path,
                 ):
        """
        :param stderr_path_created_on_demand: Must be a non-existing path that can be created as a file.
        """
        self._stderr_path_created_on_demand = stderr_path_created_on_demand
        self._executor = executor
        self._stdin = stdin
        self._stdout = stdout

    def process(self,
                settings: ProcessExecutionSettings,
                command: Command,
                ) -> ExitCodeAndStderrFile:
        """
        :return: Exit code from successful execution
        :raises ExecutionException: Either unable to execute, or execution timed out
        """
        stderr_path = self._stderr_path_created_on_demand

        with self._stdin as f_stdin:
            with self._stdout as f_stdout:
                with stderr_path.open('w') as f_stderr:
                    exit_code = self._executor.execute(
                        command,
                        settings,
                        StdFiles(
                            f_stdin,
                            StdOutputFiles(
                                f_stdout,
                                f_stderr,
                            ),
                        ),
                    )
        return ExitCodeAndStderrFile(exit_code, stderr_path)
