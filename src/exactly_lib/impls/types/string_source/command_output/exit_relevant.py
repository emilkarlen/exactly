import subprocess
from pathlib import Path
from typing import IO, TextIO

from exactly_lib.impls.types.program import top_lvl_error_msg_rendering
from exactly_lib.impls.types.string_source.contents_handler.handler_via_file import FileCreator
from exactly_lib.impls.types.string_source.contents_handler.handler_via_write_to import Writer
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.std import StdFiles, StdOutputFiles
from exactly_lib.util.file_utils.text_reader import TextFromFileReader
from exactly_lib.util.process_execution import file_ctx_managers
from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.process_execution.executors import read_stderr_on_error


class StdoutWriter(Writer):
    def __init__(self,
                 command: Command,
                 proc_exe_settings: ProcessExecutionSettings,
                 command_executor: CommandExecutor,
                 stderr_msg_reader: TextFromFileReader,
                 ):
        self._command = command
        self._proc_exe_settings = proc_exe_settings
        self._command_executor = command_executor
        self._stderr_msg_reader = stderr_msg_reader

    def write(self, tmp_file_space: DirFileSpace, output: IO):
        processor = self._processor(tmp_file_space, output)
        result = processor.process(self._proc_exe_settings, self._command)
        if result.exit_code != 0:
            raise HardErrorException(
                top_lvl_error_msg_rendering.non_zero_exit_code_msg(
                    self._command.structure_renderer(),
                    result.exit_code,
                    result.stderr,
                )
            )

    def _processor(self, tmp_file_space: DirFileSpace, output: IO,
                   ) -> read_stderr_on_error.ProcessorThatReadsStderrOnNonZeroExitCode:
        return read_stderr_on_error.ProcessorThatReadsStderrOnNonZeroExitCode(
            self._command_executor,
            tmp_file_space,
            stdin=file_ctx_managers.dev_null(),
            stdout=file_ctx_managers.opened_file(output),
            stderr_msg_reader=self._stderr_msg_reader,
        )


class StderrFileCreator(FileCreator):
    """NOTE Would like to impl in terms of write_to,
    (to avoid redundant write/read to/from separate file).
    But fails doing that because of the need to read from it
    in case of errors (as part of error message)."""

    def __init__(self,
                 command: Command,
                 proc_exe_settings: ProcessExecutionSettings,
                 command_executor: CommandExecutor,
                 stderr_msg_reader: TextFromFileReader,
                 ):
        self._command = command
        self._proc_exe_settings = proc_exe_settings
        self._command_executor = command_executor
        self._stderr_msg_reader = stderr_msg_reader

    def create(self, tmp_file_space: DirFileSpace) -> Path:
        output_path = tmp_file_space.new_path(process_output_files.STDERR_FILE_NAME)
        with output_path.open('w+') as output_f:
            exit_code = self._command_executor.execute(
                self._command,
                self._proc_exe_settings,
                StdFiles(
                    subprocess.DEVNULL,
                    StdOutputFiles(
                        subprocess.DEVNULL,
                        output_f,
                    ),
                ),
            )
            if exit_code != 0:
                raise HardErrorException(
                    top_lvl_error_msg_rendering.non_zero_exit_code_msg(
                        self._command.structure_renderer(),
                        exit_code,
                        self._err_str_from(output_f),
                    )
                )
            else:
                return output_path

    def _err_str_from(self, output: TextIO) -> str:
        output.seek(0)
        return self._stderr_msg_reader.read(output)
