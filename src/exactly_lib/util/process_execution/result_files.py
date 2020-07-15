import pathlib
from enum import Enum

from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile, FileNames


class ResultFile(Enum):
    STD_OUT = 1
    STD_ERR = 2
    EXIT_CODE = 3


RESULT_FILE_NAMES = {
    ResultFile.STD_OUT: process_output_files.STDOUT_FILE_NAME,
    ResultFile.STD_ERR: process_output_files.STDERR_FILE_NAME,
    ResultFile.EXIT_CODE: process_output_files.EXIT_CODE_FILE_NAME,
}


class DirWithResultFiles:
    """A directory that contains a file for each of the "process result files"."""

    def __init__(self, directory: pathlib.Path):
        self._directory = directory

    @property
    def directory(self) -> pathlib.Path:
        return self._directory

    @property
    def file_names(self) -> FileNames:
        return process_output_files.FILE_NAMES

    @staticmethod
    def base_name_of(output_file: ProcOutputFile) -> str:
        return process_output_files.PROC_OUTPUT_FILE_NAMES[output_file]

    def path_of_std(self, output_file: ProcOutputFile) -> pathlib.Path:
        return self._directory / self.file_names.name_of(output_file)

    def path_of_result(self, result_file: ResultFile) -> pathlib.Path:
        return self._directory / RESULT_FILE_NAMES[result_file]
