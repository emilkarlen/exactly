import subprocess

from exactly_lib.util.file_utils.std import StdFiles
from exactly_lib.util.process_execution.execution_elements import Executable, ProcessExecutionSettings


class ProcessExecutionException(Exception):
    def __init__(self, cause: Exception):
        self._cause = cause

    @property
    def cause(self) -> Exception:
        return self._cause


class ProcessExecutor:
    def execute(self,
                executable: Executable,
                settings: ProcessExecutionSettings,
                files: StdFiles,
                ) -> int:
        """
        :return: Exit code from successful execution
        :raises ExecutionException: Either unable to execute, or execution timed out
        """
        try:
            return subprocess.call(
                executable.arg_list_or_str,
                stdin=files.stdin,
                stdout=files.output.out,
                stderr=files.output.err,
                env=settings.environ,
                timeout=settings.timeout_in_seconds,
                shell=executable.is_shell,
            )
        except ValueError as ex:
            raise ProcessExecutionException(ex)
        except OSError as ex:
            raise ProcessExecutionException(ex)
        except subprocess.TimeoutExpired as ex:
            raise ProcessExecutionException(ex)
