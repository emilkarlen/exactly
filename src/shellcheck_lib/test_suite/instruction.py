import pathlib

from shellcheck_lib.document.model import Instruction


class Environment:
    def __init(self,
               suite_file_dir_path: pathlib.Path):
        self.__suite_file_dir_path = suite_file_dir_path

    @property
    def suite_file_dir_path(self) -> pathlib.Path:
        return self.__suite_file_dir_path


class FileNotAccessibleError(Exception):
    def __init__(self,
                 file_name: str):
        self._file_name = file_name

    @property
    def file_name(self) -> str:
        return self._file_name


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
