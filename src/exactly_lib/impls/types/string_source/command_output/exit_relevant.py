import subprocess
from pathlib import Path
from typing import TextIO

from exactly_lib.impls.program_execution.processors import read_stderr_on_error
from exactly_lib.impls.types.program import top_lvl_error_msg_rendering
from exactly_lib.impls.types.string_source import as_stdin
from exactly_lib.impls.types.string_source.contents.contents_via_file import FileCreator
from exactly_lib.impls.types.string_source.contents.contents_via_write_to import Writer
from exactly_lib.impls.types.utils.command_w_stdin import CommandWStdin
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.std import StdFiles, StdOutputFiles
from exactly_lib.util.file_utils.text_reader import TextFromFileReader
from exactly_lib.util.process_execution import file_ctx_managers
from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


class StdoutWriter(Writer):
    def __init__(self,
                 command: CommandWStdin,
                 proc_exe_settings: ProcessExecutionSettings,
                 command_executor: CommandExecutor,
                 stderr_msg_reader: TextFromFileReader,
                 ):
        self._command = command
        self._proc_exe_settings = proc_exe_settings
        self._command_executor = command_executor
        self._stderr_msg_reader = stderr_msg_reader

    def write(self, tmp_file_space: DirFileSpace, output: TextIO):
        processor = self._processor(tmp_file_space, output)
        result = processor.process(self._proc_exe_settings, self._command.command)
        if result.exit_code != 0:
            raise HardErrorException(
                top_lvl_error_msg_rendering.non_zero_exit_code_msg(
                    self._command.structure(),
                    result.exit_code,
                    result.stderr,
                )
            )

    def _processor(self,
                   tmp_file_space: DirFileSpace,
                   output: TextIO,
                   ) -> read_stderr_on_error.ProcessorThatReadsStderrOnNonZeroExitCode:
        return read_stderr_on_error.ProcessorThatReadsStderrOnNonZeroExitCode(
            self._command_executor,
            tmp_file_space,
            stdin=as_stdin.of_sequence(self._command.stdin, mem_buff_size=0),
            stdout=file_ctx_managers.opened_file(output),
            stderr_msg_reader=self._stderr_msg_reader,
        )


class StderrFileCreator(FileCreator):
    """NOTE Would like to impl in terms of write_to,
    (to avoid redundant write/read to/from separate file).
    But fails doing that because of the need to read from it
    in case of errors (as part of error message)."""

    def __init__(self,
                 command: CommandWStdin,
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
            exit_code = self._execute(output_f)
            if exit_code != 0:
                self._raise_hard_error(exit_code, output_f)
            else:
                return output_path

    def _execute(self, output_file: TextIO) -> int:
        with as_stdin.of_sequence(self._command.stdin, mem_buff_size=0) as stdin_f:
            std_files = StdFiles(
                stdin_f,
                StdOutputFiles(subprocess.DEVNULL, output_file),
            )
            return self._command_executor.execute(
                self._command.command,
                self._proc_exe_settings,
                std_files,
            )

    def _raise_hard_error(self,
                          exit_code: int,
                          stderr: TextIO,
                          ):
        raise HardErrorException(
            top_lvl_error_msg_rendering.non_zero_exit_code_msg(
                self._command.structure(),
                exit_code,
                self._err_str_from(stderr),
            )
        )

    def _err_str_from(self, output: TextIO) -> str:
        output.seek(0)
        return self._stderr_msg_reader.read(output)
