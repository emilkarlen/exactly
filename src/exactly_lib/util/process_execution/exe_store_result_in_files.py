import pathlib
from typing import ContextManager

from exactly_lib.util.file_utils import ensure_file_existence
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings, Executable
from .process_executor import ProcessExecutor, ProcessExecutionFile, ExecutableExecutor
from .result_files import ResultFile, DirWithResultFiles


class ExecutorThatStoresResultInFilesInDir(ExecutableExecutor[int]):
    """An object must only be used for a single execution."""

    def __init__(self,
                 executor: ProcessExecutor,
                 storage_dir: pathlib.Path,
                 stdin: ContextManager[ProcessExecutionFile],
                 ):
        """
        :param storage_dir: Must be a directory that does not contain a file
        with any of the process output file names.
        """
        self._storage_dir = DirWithResultFiles(storage_dir)
        self._executor = executor
        self._stdin = stdin

    @property
    def storage_dir(self) -> DirWithResultFiles:
        return self._storage_dir

    def execute(self,
                settings: ProcessExecutionSettings,
                executable: Executable,
                ) -> int:
        """
        :return: Exit code from successful execution
        :raises ExecutionException: Either unable to execute, or execution timed out
        """
        storage_dir = self._storage_dir
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

        return exit_code
