import pathlib
from typing import Optional, ContextManager

from exactly_lib.impls.program_execution.command_processor import CommandProcessor
from exactly_lib.impls.program_execution.processors import store_result_in_files
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.std import ProcessExecutionFile, StdFiles, StdOutputFiles
from exactly_lib.util.file_utils.text_reader import TextFromFileReader
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.process_execution.result_files import ResultFile, DirWithResultFiles


class Result(tuple):
    def __new__(cls,
                exit_code: int,
                stderr: Optional[str],
                ):
        return tuple.__new__(cls, (exit_code,
                                   stderr))

    @property
    def exit_code(self) -> int:
        return self[0]

    @property
    def stderr(self) -> Optional[str]:
        return self[1]


class ResultWithFiles(tuple):
    def __new__(cls,
                exit_code: int,
                stderr: Optional[str],
                files: DirWithResultFiles,
                ):
        return tuple.__new__(cls, (exit_code,
                                   stderr,
                                   files))

    @property
    def exit_code(self) -> int:
        return self[0]

    @property
    def stderr(self) -> Optional[str]:
        return self[1]

    @property
    def files(self) -> DirWithResultFiles:
        return self[2]

    @property
    def stderr_file(self) -> pathlib.Path:
        return self[2].path_of_std(ProcOutputFile.STDERR)


class ProcessorThatStoresResultInFilesInDirAndReadsStderrOnNonZeroExitCode(CommandProcessor[ResultWithFiles]):
    """An object must only be used for a single execution."""

    def __init__(self,
                 executor: CommandExecutor,
                 storage_dir: pathlib.Path,
                 stdin: ContextManager[ProcessExecutionFile],
                 stderr_msg_reader: TextFromFileReader,
                 ):
        self._executor = store_result_in_files.ProcessorThatStoresResultInFilesInDir(executor, storage_dir, stdin)
        self._stderr_msg_reader = stderr_msg_reader

    @property
    def storage_dir(self) -> DirWithResultFiles:
        return self._executor.storage_dir

    def process(self,
                settings: ProcessExecutionSettings,
                command: Command,
                ) -> ResultWithFiles:
        """
        :return: Result has stderr contents iff exit code != 0
        :raises ExecutionException: Either unable to execute, or execution timed out
        """
        result = self._executor.process(settings, command)

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


class ProcessorThatReadsStderrOnNonZeroExitCode(CommandProcessor[Result]):
    """An object must only be used for a single execution."""

    def __init__(self,
                 executor: CommandExecutor,
                 tmp_file_space: DirFileSpace,
                 stdin: ContextManager[ProcessExecutionFile],
                 stdout: ContextManager[ProcessExecutionFile],
                 stderr_msg_reader: TextFromFileReader,
                 ):
        self._executor = executor
        self._tmp_file_space = tmp_file_space
        self._stdin = stdin
        self._stdout = stdout
        self._stderr_msg_reader = stderr_msg_reader

    def process(self,
                settings: ProcessExecutionSettings,
                command: Command,
                ) -> Result:
        """
        :return: Result has stderr contents iff exit code != 0
        :raises ExecutionException: Either unable to execute, or execution timed out
        """
        std_err_path = self._tmp_file_space.new_path('stderr')
        with std_err_path.open('w') as stderr_f:
            with self._stdout as stdout_f:
                with self._stdin as stdin_f:
                    exit_code = self._executor.execute(
                        command,
                        settings,
                        StdFiles(
                            stdin_f,
                            StdOutputFiles(stdout_f,
                                           stderr_f)
                        ),
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
