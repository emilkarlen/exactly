import pathlib

from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.process_execution.process_output_files import FileNames


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
        return process_output_files.FILE_NAMES

    def path_of(self, output_file: process_output_files.ProcOutputFile) -> pathlib.Path:
        return self.output_dir_path / self.file_names.name_of(output_file)
