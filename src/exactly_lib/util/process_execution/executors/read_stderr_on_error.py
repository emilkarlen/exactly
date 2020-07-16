import pathlib
import subprocess
from typing import Optional, ContextManager

from exactly_lib.util.file_utils.tmp_file_space import TmpDirFileSpace
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings, Executable
from exactly_lib.util.process_execution.process_executor import ProcessExecutor, ProcessExecutionFile, \
    ExecutableExecutor
from exactly_lib.util.process_execution.result_files import ResultFile, DirWithResultFiles
from . import store_result_in_files
from ...file_utils.text_reader import TextFromFileReader


class Result:
    def __init__(self,
                 exit_code: int,
                 stderr: Optional[str],
                 ):
        self.exit_code = exit_code
        self.stderr = stderr


class ResultWithFiles:
    def __init__(self,
                 exit_code: int,
                 stderr: Optional[str],
                 files: DirWithResultFiles,
                 ):
        self.exit_code = exit_code
        self.stderr = stderr
        self.files = files


class ExecutorThatStoresResultInFilesInDirAndReadsStderrOnNonZeroExitCode(ExecutableExecutor[ResultWithFiles]):
    """An object must only be used for a single execution."""

    def __init__(self,
                 executor: ProcessExecutor,
                 storage_dir: pathlib.Path,
                 stdin: ContextManager[ProcessExecutionFile],
                 stderr_msg_reader: TextFromFileReader,
                 ):
        self._executor = store_result_in_files.ExecutorThatStoresResultInFilesInDir(executor, storage_dir, stdin)
        self._stderr_msg_reader = stderr_msg_reader

    @property
    def storage_dir(self) -> DirWithResultFiles:
        return self._executor.storage_dir

    def execute(self,
                settings: ProcessExecutionSettings,
                executable: Executable,
                ) -> ResultWithFiles:
        """
        :return: Result has stderr contents iff exit code != 0
        :raises ExecutionException: Either unable to execute, or execution timed out
        """
        result = self._executor.execute(settings, executable)

        return ResultWithFiles(
            result.exit_code,
            self._stderr_for(result),
            result.files,
        )

    def _stderr_for(self, result: store_result_in_files.ExitCodeAndFiles) -> Optional[str]:
        if result.exit_code == 0:
            return None

        with result.files.path_of_result(ResultFile.STD_ERR).open('r') as f:
            return self._stderr_msg_reader.read(f)


class ExecutorThatReadsStderrOnNonZeroExitCode(ExecutableExecutor[Result]):
    """An object must only be used for a single execution."""

    def __init__(self,
                 executor: ProcessExecutor,
                 tmp_file_space: TmpDirFileSpace,
                 stdin: ContextManager[ProcessExecutionFile],
                 stderr_msg_reader: TextFromFileReader,
                 ):
        self._executor = executor
        self._tmp_file_space = tmp_file_space
        self._stdin = stdin
        self._stderr_msg_reader = stderr_msg_reader

    def execute(self,
                settings: ProcessExecutionSettings,
                executable: Executable,
                ) -> Result:
        """
        :return: Result has stderr contents iff exit code != 0
        :raises ExecutionException: Either unable to execute, or execution timed out
        """
        std_err_path = self._tmp_file_space.new_path('stderr')
        with std_err_path.open('w') as stderr_f:
            with self._stdin as stdin_f:
                exit_code = self._executor.execute(
                    executable,
                    settings,
                    stdin=stdin_f,
                    stdout=subprocess.DEVNULL,
                    stderr=stderr_f,
                )

        return Result(
            exit_code,
            self._stderr_for(exit_code, std_err_path),
        )

    def _stderr_for(self, exit_code: int, stderr_path: pathlib.Path) -> Optional[str]:
        if exit_code == 0:
            return None

        with stderr_path.open('r') as f:
            return self._stderr_msg_reader.read(f)