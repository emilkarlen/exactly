import os
import pathlib
import subprocess

from exactly_lib.util import file_utils
from exactly_lib.util.file_utils import write_new_text_file
from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings, Executable
from exactly_lib.util.process_execution.process_output_files import FileNames


class Result(tuple):
    def __new__(cls,
                error_message: str,
                exit_code: int,
                output_dir_path: pathlib.Path):
        return tuple.__new__(cls, (error_message,
                                   exit_code,
                                   output_dir_path))

    @property
    def is_success(self) -> bool:
        return self.error_message is None

    @property
    def error_message(self) -> str:
        return self[0]

    @property
    def exit_code(self) -> int:
        return self[1]

    @property
    def output_dir_path(self) -> pathlib.Path:
        return self[2]

    @property
    def file_names(self) -> FileNames:
        return process_output_files.FILE_NAMES

    def path_of(self, output_file: process_output_files.ProcOutputFile) -> pathlib.Path:
        return self.output_dir_path / self.file_names.name_of(output_file)


class ResultAndStderr:
    def __init__(self,
                 result: Result,
                 stderr_contents: str):
        self.result = result
        self.stderr_contents = stderr_contents


class ExecutorThatStoresResultInFilesInDir:
    def __init__(self, process_execution_settings: ProcessExecutionSettings):
        self.process_execution_settings = process_execution_settings

    def execute(self,
                storage_dir: pathlib.Path,
                executable: Executable) -> Result:

        def _err_msg(exception: Exception) -> str:
            return 'Error executing process:\n\n' + str(exception)

        file_utils.ensure_directory_exists_as_a_directory__impl_error(storage_dir)
        with open(str(storage_dir / process_output_files.STDOUT_FILE_NAME), 'w') as f_stdout:
            with open(str(storage_dir / process_output_files.STDERR_FILE_NAME), 'w') as f_stderr:
                try:
                    exit_code = subprocess.call(executable.arg_list_or_str,
                                                stdin=subprocess.DEVNULL,
                                                stdout=f_stdout,
                                                stderr=f_stderr,
                                                env=self.process_execution_settings.environ,
                                                timeout=self.process_execution_settings.timeout_in_seconds,
                                                shell=executable.is_shell)
                    write_new_text_file(storage_dir / process_output_files.EXIT_CODE_FILE_NAME,
                                        str(exit_code))
                    return Result(None,
                                  exit_code,
                                  storage_dir)
                except ValueError as ex:
                    msg = _err_msg(ex)
                    return Result(msg, None, None)
                except OSError as ex:
                    msg = _err_msg(ex)
                    return Result(msg, None, None)
                except subprocess.TimeoutExpired as ex:
                    msg = _err_msg(ex)
                    return Result(msg, None, None)


def read_stderr_if_non_zero_exitcode(result: Result) -> ResultAndStderr:
    stderr_contents = None
    if result.is_success and result.exit_code != 0:
        stderr_contents = file_utils.contents_of(result.output_dir_path / result.file_names.stderr)
    return ResultAndStderr(result, stderr_contents)


def failure_message_for_failure_to_failure_to_execute_process(result_and_err: ResultAndStderr) -> str:
    return 'Failed to execute sub process: ' + result_and_err.result.error_message


def failure_message_for_nonzero_status(result_and_err: ResultAndStderr) -> str:
    msg_tail = ''
    if result_and_err.stderr_contents:
        msg_tail = os.linesep + result_and_err.stderr_contents
    return 'Exit code: {}{}'.format(result_and_err.result.exit_code, msg_tail)


def result_for_non_success_or_non_zero_exit_code(result_and_err: ResultAndStderr) -> str:
    if result_and_err.result.is_success:
        if result_and_err.result.exit_code == 0:
            return None
        else:
            return failure_message_for_nonzero_status(result_and_err)
    else:
        return failure_message_for_failure_to_failure_to_execute_process(result_and_err)


def execute_and_read_stderr_if_non_zero_exitcode(executable: Executable,
                                                 executor: ExecutorThatStoresResultInFilesInDir,
                                                 storage_dir: pathlib.Path) -> ResultAndStderr:
    result = executor.execute(storage_dir, executable)
    return read_stderr_if_non_zero_exitcode(result)
