import os
import pathlib
import subprocess

from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.phases.common import PhaseLoggingPaths
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case_utils import file_services
from exactly_lib.util import file_utils
from exactly_lib.util.file_utils import write_new_text_file
from exactly_lib.util.process_execution.os_process_execution import ProcessExecutionSettings

EXIT_CODE_FILE_NAME = 'exitcode'
STDOUT_FILE_NAME = 'stdout'
STDERR_FILE_NAME = 'stderr'


class FileNames:
    @property
    def exit_code(self) -> str:
        return EXIT_CODE_FILE_NAME

    @property
    def stdout(self) -> str:
        return STDOUT_FILE_NAME

    @property
    def stderr(self) -> str:
        return STDERR_FILE_NAME


FILE_NAMES = FileNames()


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
        return FILE_NAMES


class ResultAndStderr:
    def __init__(self,
                 result: Result,
                 stderr_contents: str):
        self.result = result
        self.stderr_contents = stderr_contents


class InstructionSourceInfo(tuple):
    def __new__(cls,
                source_line_number: int,
                instruction_name: str):
        return tuple.__new__(cls, (source_line_number,
                                   instruction_name))

    @property
    def instruction_name(self) -> str:
        return self[1]

    @property
    def line_number(self) -> int:
        return self[0]


class CmdAndArgsResolver:
    """
    Resolves the command string to execute.
    """

    @property
    def symbol_usages(self) -> list:
        return []

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds):
        """
        Resolves the "thing" to execute by Python's subprocess module.

        :return: Either a string or a list consisting of the name of the command
        followed by arguments.
        """
        raise NotImplementedError()


class ExecutorThatStoresResultInFilesInDir:
    def __init__(self,
                 is_shell: bool,
                 process_execution_settings: ProcessExecutionSettings):
        self.is_shell = is_shell
        self.process_execution_settings = process_execution_settings

    def apply(self,
              storage_dir: pathlib.Path,
              cmd_and_args) -> Result:

        def _err_msg(exception: Exception) -> str:
            return 'Error executing process:\n' + str(exception)

        file_services.ensure_directory_exists_as_a_directory(storage_dir)
        with open(str(storage_dir / STDOUT_FILE_NAME), 'w') as f_stdout:
            with open(str(storage_dir / STDERR_FILE_NAME), 'w') as f_stderr:
                try:
                    exit_code = subprocess.call(cmd_and_args,
                                                stdin=subprocess.DEVNULL,
                                                stdout=f_stdout,
                                                stderr=f_stderr,
                                                env=self.process_execution_settings.environ,
                                                timeout=self.process_execution_settings.timeout_in_seconds,
                                                shell=self.is_shell)
                    write_new_text_file(storage_dir / EXIT_CODE_FILE_NAME,
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


def failure_message_for_nonzero_status(result_and_err: ResultAndStderr) -> str:
    msg_tail = ''
    if result_and_err.stderr_contents:
        msg_tail = os.linesep + result_and_err.stderr_contents
    return 'Exit code: {}{}'.format(result_and_err.result.exit_code, msg_tail)


class ExecuteInfo:
    def __init__(self,
                 instruction_source_info: InstructionSourceInfo,
                 command):
        self.instruction_source_info = instruction_source_info
        self.command = command


def execute_and_read_stderr_if_non_zero_exitcode(execute_info: ExecuteInfo,
                                                 executor: ExecutorThatStoresResultInFilesInDir,
                                                 phase_logging_paths: PhaseLoggingPaths) -> ResultAndStderr:
    source_info = execute_info.instruction_source_info
    storage_dir = instruction_log_dir(phase_logging_paths, source_info)
    result = executor.apply(storage_dir, execute_info.command)
    return read_stderr_if_non_zero_exitcode(result)


def instruction_log_dir(phase_logging_paths: PhaseLoggingPaths,
                        source_info: InstructionSourceInfo) -> pathlib.Path:
    return phase_logging_paths.for_line(source_info.line_number, source_info.instruction_name)


def result_to_sh(result_and_stderr: ResultAndStderr) -> sh.SuccessOrHardError:
    result = result_and_stderr.result
    if not result.is_success:
        return sh.new_sh_hard_error(result.error_message)
    if result.exit_code != 0:
        return sh.new_sh_hard_error(failure_message_for_nonzero_status(result_and_stderr))
    return sh.new_sh_success()


def result_to_pfh(result_and_stderr: ResultAndStderr) -> pfh.PassOrFailOrHardError:
    result = result_and_stderr.result
    if not result.is_success:
        return pfh.new_pfh_hard_error(failure_message_for_nonzero_status(result_and_stderr))
    if result.exit_code != 0:
        return pfh.new_pfh_fail(failure_message_for_nonzero_status(result_and_stderr))
    return pfh.new_pfh_pass()
