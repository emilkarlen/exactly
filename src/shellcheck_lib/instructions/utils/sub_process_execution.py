import os
import pathlib
import subprocess

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure, log_phase_dir
from shellcheck_lib.general import file_utils
from shellcheck_lib.general.file_utils import write_new_text_file
from shellcheck_lib.instructions.utils import file_services
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh

EXIT_CODE_FILE_NAME = 'exitcode'
STDOUT_FILE_NAME = 'stdout'
STDERR_FILE_NAME = 'stderr'


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
    def exit_code_file_name(self) -> str:
        return EXIT_CODE_FILE_NAME

    @property
    def stdout_file_name(self) -> str:
        return STDOUT_FILE_NAME

    @property
    def stderr_file_name(self) -> str:
        return STDERR_FILE_NAME


class ResultAndStderr:
    def __init__(self,
                 result: Result,
                 stderr_contents: str):
        self.result = result
        self.stderr_contents = stderr_contents


class InstructionMetaInfo(tuple):
    def __new__(cls,
                phase_name: str,
                instruction_name: str):
        return tuple.__new__(cls, (phase_name,
                                   instruction_name))

    @property
    def phase_name(self) -> str:
        return self[0]

    @property
    def instruction_name(self) -> str:
        return self[1]


class InstructionSourceInfo(tuple):
    def __new__(cls,
                instruction_meta_info: InstructionMetaInfo,
                source_line_number: int):
        return tuple.__new__(cls, (instruction_meta_info,
                                   source_line_number))

    @property
    def meta_info(self) -> InstructionMetaInfo:
        return self[0]

    @property
    def line_number(self) -> int:
        return self[1]


class Executor:
    def apply(self,
              instruction_source_info: InstructionSourceInfo,
              eds: ExecutionDirectoryStructure,
              cmd_and_args) -> Result:
        raise NotImplementedError()


class ExecutorThatLogsResultUnderPhaseDir(Executor):
    def __init__(self,
                 is_shell: bool):
        self.is_shell = is_shell

    def apply(self,
              instruction_source_info: InstructionSourceInfo,
              eds: ExecutionDirectoryStructure,
              cmd_and_args) -> Result:

        def _err_msg(exception: Exception) -> str:
            return 'Error executing %s instruction in subprocess: "%s"' % (
                instruction_source_info.meta_info.instruction_name,
                str(exception))

        output_dir = self.instruction_output_directory(eds, instruction_source_info)
        file_services.create_dir_that_is_expected_to_not_exist(output_dir)
        with open(str(output_dir / STDOUT_FILE_NAME), 'w') as f_stdout:
            with open(str(output_dir / STDERR_FILE_NAME), 'w') as f_stderr:
                try:
                    exit_code = subprocess.call(cmd_and_args,
                                                stdin=subprocess.DEVNULL,
                                                stdout=f_stdout,
                                                stderr=f_stderr,
                                                shell=self.is_shell)
                    write_new_text_file(output_dir / EXIT_CODE_FILE_NAME,
                                        str(exit_code))
                    return Result(None,
                                  exit_code,
                                  output_dir)
                except ValueError as ex:
                    msg = _err_msg(ex)
                    return Result(msg, None, None)
                except OSError as ex:
                    msg = _err_msg(ex)
                    return Result(msg, None, None)

    def instruction_output_directory(self,
                                     eds: ExecutionDirectoryStructure,
                                     info: InstructionSourceInfo) -> pathlib.Path:
        instruction_sub_dir = self._format_instruction_output_sub_dir_name(info.meta_info.instruction_name,
                                                                           info.line_number)
        return log_phase_dir(eds, info.meta_info.phase_name) / instruction_sub_dir

    @staticmethod
    def _format_instruction_output_sub_dir_name(instruction_name: str,
                                                line_number: int) -> str:
        return '%03d-%s' % (line_number, instruction_name)


def read_stderr_if_non_zero_exitcode(result: Result) -> ResultAndStderr:
    stderr_contents = None
    if result.is_success and result.exit_code != 0:
        stderr_contents = file_utils.contents_of(result.output_dir_path / result.stderr_file_name)
    return ResultAndStderr(result, stderr_contents)


def apply_and_read_stderr_if_non_zero_exitcode(executor: ExecutorThatLogsResultUnderPhaseDir,
                                               instruction_source_info: InstructionSourceInfo,
                                               eds: ExecutionDirectoryStructure,
                                               cmd_and_args: list) -> ResultAndStderr:
    result = executor.apply(instruction_source_info, eds, cmd_and_args)
    return read_stderr_if_non_zero_exitcode(result)


def failure_message_for_nonzero_status(result_and_err: ResultAndStderr) -> str:
    msg_tail = ''
    if result_and_err.stderr_contents:
        msg_tail = os.linesep + result_and_err.stderr_contents
    return 'Exit code {}{}'.format(result_and_err.result.exit_code, msg_tail)


class ExecuteInfo:
    def __init__(self,
                 instruction_source_info: InstructionSourceInfo,
                 command):
        self.instruction_source_info = instruction_source_info
        self.command = command


def execute_and_return_sh(execute_info: ExecuteInfo,
                          executor: ExecutorThatLogsResultUnderPhaseDir,
                          eds: ExecutionDirectoryStructure) -> sh.SuccessOrHardError:
    result_and_stderr = _execute(execute_info, executor, eds)
    result = result_and_stderr.result
    if result.is_success and result.exit_code != 0:
        return sh.new_sh_hard_error(failure_message_for_nonzero_status(result_and_stderr))
    return sh.new_sh_success()


def execute_and_return_pfh(execute_info: ExecuteInfo,
                           executor: ExecutorThatLogsResultUnderPhaseDir,
                           eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
    result_and_stderr = _execute(execute_info, executor, eds)
    result = result_and_stderr.result
    if not result.is_success:
        return pfh.new_pfh_hard_error(failure_message_for_nonzero_status(result_and_stderr))
    if result.exit_code != 0:
        return pfh.new_pfh_fail(failure_message_for_nonzero_status(result_and_stderr))
    return pfh.new_pfh_pass()


def _execute(execute_info: ExecuteInfo,
             executor: ExecutorThatLogsResultUnderPhaseDir,
             eds: ExecutionDirectoryStructure) -> ResultAndStderr:
    result = executor.apply(execute_info.instruction_source_info, eds, execute_info.command)
    return read_stderr_if_non_zero_exitcode(result)
