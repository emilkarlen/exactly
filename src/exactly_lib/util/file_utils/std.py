import subprocess
import sys
from typing import Union, TextIO

from exactly_lib.util.process_execution.process_output_files import ProcOutputFile

ProcessExecutionFile = Union[None, int, TextIO]


class StdOutputFiles(tuple):

    def __new__(cls,
                stdout_file: ProcessExecutionFile = sys.stdout,
                stderr_file: ProcessExecutionFile = sys.stderr):
        return tuple.__new__(cls, (stdout_file, stderr_file))

    @property
    def out(self) -> ProcessExecutionFile:
        return self[0]

    @property
    def err(self) -> ProcessExecutionFile:
        return self[1]

    def get(self, file: ProcOutputFile) -> ProcessExecutionFile:
        return (
            self[0]
            if file is ProcOutputFile.STDOUT
            else
            self[1]
        )


class StdOutputFilesContents(tuple):
    def __new__(cls,
                out: str,
                err: str):
        return tuple.__new__(cls, (out, err))

    @staticmethod
    def empty() -> 'StdOutputFilesContents':
        return StdOutputFilesContents('', '')

    @property
    def out(self) -> str:
        return self[0]

    @property
    def err(self) -> str:
        return self[1]


def new_std_output_files_dev_null() -> StdOutputFiles:
    return StdOutputFiles(subprocess.DEVNULL,
                          subprocess.DEVNULL)


class StdFiles(tuple):
    def __new__(cls,
                stdin_file: ProcessExecutionFile = sys.stdin,
                output_files: StdOutputFiles = StdOutputFiles()):
        return tuple.__new__(cls, (stdin_file, output_files))

    @property
    def stdin(self) -> ProcessExecutionFile:
        return self[0]

    @property
    def output(self) -> StdOutputFiles:
        return self[1]


def std_files_dev_null() -> StdFiles:
    return StdFiles(subprocess.DEVNULL,
                    new_std_output_files_dev_null())
