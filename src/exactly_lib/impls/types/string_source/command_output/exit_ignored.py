import subprocess
from abc import ABC, abstractmethod
from typing import TextIO

from exactly_lib.impls.types.string_source import as_stdin
from exactly_lib.impls.types.string_source.contents.contents_via_write_to import Writer
from exactly_lib.impls.types.utils.command_w_stdin import CommandWStdin
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.std import StdFiles, StdOutputFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


class _WriterBase(Writer, ABC):
    def __init__(self,
                 command: CommandWStdin,
                 proc_exe_settings: ProcessExecutionSettings,
                 command_executor: CommandExecutor,
                 ):
        self._command = command
        self._proc_exe_settings = proc_exe_settings
        self._command_executor = command_executor

    def write(self, tmp_file_space: DirFileSpace, output: TextIO):
        with as_stdin.of_sequence(self._command.stdin, mem_buff_size=0) as stdin_f:
            std_files = StdFiles(stdin_f, self._output_files(output))
            self._command_executor.execute(
                self._command.command,
                self._proc_exe_settings,
                std_files,
            )

    @abstractmethod
    def _output_files(self, output: TextIO) -> StdOutputFiles:
        pass


class StdoutWriter(_WriterBase):
    def _output_files(self, output: TextIO) -> StdOutputFiles:
        return StdOutputFiles(
            output,
            subprocess.DEVNULL,
        )


class StderrWriter(_WriterBase):
    def _output_files(self, output: TextIO) -> StdOutputFiles:
        return StdOutputFiles(
            subprocess.DEVNULL,
            output,
        )
