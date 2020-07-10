import pathlib
from typing import Optional, ContextManager

from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings, Executable
from .exe_store_result_in_files import ExecutorThatStoresResultInFilesInDir
from .process_executor import ProcessExecutor, ProcessExecutionFile
from .result_files import ResultFile, DirWithResultFiles


class Result:
    def __init__(self,
                 exit_code: int,
                 stderr: Optional[str],
                 ):
        self.exit_code = exit_code
        self.stderr = stderr


class ExecutorThatStoresResultInFilesInDirAndReadsStderrOnNonZeroExitCode:
    """An object must only be used for a single execution."""

    def __init__(self,
                 executor: ProcessExecutor,
                 storage_dir: pathlib.Path,
                 stdin: ContextManager[ProcessExecutionFile],
                 max_stderr_to_read: int = 1000
                 ):
        self._executor = ExecutorThatStoresResultInFilesInDir(executor, storage_dir, stdin)
        self._max_stderr_to_read = max_stderr_to_read

    @property
    def storage_dir(self) -> DirWithResultFiles:
        return self._executor.storage_dir

    def execute(self,
                settings: ProcessExecutionSettings,
                executable: Executable,
                ) -> Result:
        """
        :return: Result has stderr contents iff exit code != 0
        :raises ExecutionException: Either unable to execute, or execution timed out
        """
        exit_code = self._executor.execute(settings, executable)

        return Result(
            exit_code,
            self._stderr_for(exit_code),
        )

    def _stderr_for(self, exit_code: int) -> Optional[str]:
        if exit_code == 0:
            return None

        with self.storage_dir.path_of_result(ResultFile.STD_ERR).open('r') as f:
            return f.read(self._max_stderr_to_read)
