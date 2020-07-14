import subprocess
from abc import ABC, abstractmethod
from typing import IO, Union, TypeVar, Generic

from exactly_lib.util.process_execution.execution_elements import Executable, ProcessExecutionSettings


class ProcessExecutionException(Exception):
    def __init__(self, cause: Exception):
        self._cause = cause

    @property
    def cause(self) -> Exception:
        return self._cause


ProcessExecutionFile = Union[None, int, IO]


class ProcessExecutor:
    def execute(self,
                executable: Executable,
                settings: ProcessExecutionSettings,
                stdin: ProcessExecutionFile,
                stdout: ProcessExecutionFile,
                stderr: ProcessExecutionFile,
                ) -> int:
        """
        :return: Exit code from successful execution
        :raises ExecutionException: Either unable to execute, or execution timed out
        """
        try:
            return subprocess.call(
                executable.arg_list_or_str,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
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


T = TypeVar('T')


class ExecutableExecutor(Generic[T], ABC):
    @abstractmethod
    def execute(self,
                settings: ProcessExecutionSettings,
                executable: Executable,
                ) -> T:
        """
        :raises ProcessExecutionException: Unable to execute the program.
        """
        pass
