import pathlib

from shellcheck_lib.document.model import Instruction


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


class TestCaseSectionInstruction(Instruction):
    def resolve_paths(self,
                      environment: Environment) -> list:
        """
        :raises FileNotAccessibleError: A referenced file is not accessible.
        :return: [pathlib.Path]
        """
        raise NotImplementedError()


class TestSuiteSectionInstruction(Instruction):
    def resolve_paths(self,
                      environment: Environment) -> list:
        """
        :raises FileNotAccessibleError: A referenced file is not accessible.
        :return: [pathlib.Path]
        """
        raise NotImplementedError()
