import pathlib
import subprocess

from exactly_lib.util.file_utils import ensure_file_existence, misc_utils
from exactly_lib.util.file_utils.misc_utils import write_new_text_file
from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings, Executable
from .result import Result, ResultAndStderr


class ExecutorThatStoresResultInFilesInDir:
    def __init__(self, process_execution_settings: ProcessExecutionSettings):
        self.process_execution_settings = process_execution_settings

    def execute(self,
                storage_dir: pathlib.Path,
                executable: Executable) -> Result:

        def _err_msg(exception: Exception) -> str:
            return str(exception)

        ensure_file_existence.ensure_directory_exists_as_a_directory__impl_error(storage_dir)
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
        stderr_contents = misc_utils.contents_of(result.output_dir_path / result.file_names.stderr)
    return ResultAndStderr(result, stderr_contents)


def execute_and_read_stderr_if_non_zero_exitcode(executable: Executable,
                                                 executor: ExecutorThatStoresResultInFilesInDir,
                                                 storage_dir: pathlib.Path) -> ResultAndStderr:
    result = executor.execute(storage_dir, executable)
    return read_stderr_if_non_zero_exitcode(result)
