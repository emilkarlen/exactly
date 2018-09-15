import pathlib
from typing import List

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


class TestSuiteFileReferencesInstruction(TestSuiteInstruction):
    def resolve_paths(self, environment: Environment) -> List[pathlib.Path]:
        """
        :raises FileNotAccessibleSimpleError: A referenced file is not accessible.
        """
        raise NotImplementedError('abstract method')


class FileNotAccessibleSimpleError(Exception):
    def __init__(self,
                 file_path: pathlib.Path,
                 error_message_header: str):
        self._file_path = file_path
        self._error_message_header = error_message_header

    @property
    def file_path(self) -> pathlib.Path:
        return self._file_path

    @property
    def error_message_header(self) -> str:
        return self._error_message_header
