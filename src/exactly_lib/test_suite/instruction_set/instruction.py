import pathlib

from exactly_lib.section_document.model import Instruction


class TestSuiteInstruction(Instruction):
    pass


class Environment:
    def __init__(self,
                 suite_file_dir_path: pathlib.Path):
        self.__suite_file_dir_path = suite_file_dir_path

    @property
    def suite_file_dir_path(self) -> pathlib.Path:
        return self.__suite_file_dir_path


class FileNotAccessibleSimpleError(Exception):
    def __init__(self,
                 file_path: pathlib.Path):
        self._file_path = file_path

    @property
    def file_path(self) -> pathlib.Path:
        return self._file_path
