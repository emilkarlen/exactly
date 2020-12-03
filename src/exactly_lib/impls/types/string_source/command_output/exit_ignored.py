import subprocess
from abc import ABC, abstractmethod
from typing import IO

from exactly_lib.impls.types.string_source.contents_handler.handler_via_write_to import Writer
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.std import StdFiles, StdOutputFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


class _WriterBase(Writer, ABC):
    def __init__(self,
                 command: Command,
                 proc_exe_settings: ProcessExecutionSettings,
                 command_executor: CommandExecutor,
                 ):
        self._command = command
        self._proc_exe_settings = proc_exe_settings
        self._command_executor = command_executor

    def write(self, tmp_file_space: DirFileSpace, output: IO):
        self._command_executor.execute(
            self._command,
            self._proc_exe_settings,
            StdFiles(
                subprocess.DEVNULL,
                self._output_files(output),
            ),
        )

    @abstractmethod
    def _output_files(self, output: IO) -> StdOutputFiles:
        pass


class StdoutWriter(_WriterBase):
    def _output_files(self, output: IO) -> StdOutputFiles:
        return StdOutputFiles(
            output,
            subprocess.DEVNULL,
        )


class StderrWriter(_WriterBase):
    def _output_files(self, output: IO) -> StdOutputFiles:
        return StdOutputFiles(
            subprocess.DEVNULL,
            output,
        )
