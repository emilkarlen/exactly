import pathlib
from typing import ContextManager

from exactly_lib.util.file_utils import ensure_file_existence
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings, Executable
from exactly_lib.util.process_execution.process_executor import ProcessExecutor, ProcessExecutionFile, \
    ExecutableExecutor
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


class ExecutorThatStoresResultInFilesInDir(ExecutableExecutor[ExitCodeAndFiles]):
    """An object must only be used for a single execution."""

    def __init__(self,
                 executor: ProcessExecutor,
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

    def execute(self,
                settings: ProcessExecutionSettings,
                executable: Executable,
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
                        executable,
                        settings,
                        stdin=f_stdin,
                        stdout=f_stdout,
                        stderr=f_stderr,
                    )
        with exit_code_path.open('w') as exit_code_f:
            exit_code_f.write(str(exit_code))

        return ExitCodeAndFiles(exit_code, self._storage_dir_created_on_demand)
