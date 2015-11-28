import pathlib
import subprocess

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure, log_phase_dir
from shellcheck_lib.general.file_utils import write_new_text_file
from shellcheck_lib.instructions.utils import file_services

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
              cmd_and_args: list) -> Result:
        raise NotImplementedError()


class ExecutorThatLogsResultUnderPhaseDir(Executor):
    def apply(self,
              instruction_source_info: InstructionSourceInfo,
              eds: ExecutionDirectoryStructure,
              cmd_and_args: list) -> Result:
        output_dir = self.instruction_output_directory(eds, instruction_source_info)
        file_services.create_dir_that_is_expected_to_not_exist(output_dir)
        with open(str(output_dir / STDOUT_FILE_NAME), 'w') as f_stdout:
            with open(str(output_dir / STDERR_FILE_NAME), 'w') as f_stderr:
                try:
                    exit_code = subprocess.call(cmd_and_args,
                                                stdin=subprocess.DEVNULL,
                                                stdout=f_stdout,
                                                stderr=f_stderr)
                    write_new_text_file(output_dir / EXIT_CODE_FILE_NAME,
                                        str(exit_code))
                    return Result(None,
                                  exit_code,
                                  output_dir)
                except ValueError as ex:
                    msg = 'Error executing act phase as subprocess: ' + str(ex)
                    return Result(msg, None, None)
                except OSError as ex:
                    msg = 'Error executing act phase as subprocess: ' + str(ex)
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
