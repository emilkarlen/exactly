import pathlib

from shellcheck_lib.document.model import Instruction
from shellcheck_lib.test_suite.structure import TestSuite


class Environment:
    def __init(self,
               suite_file_dir_path: pathlib.Path):
        self.__suite_file_dir_path = suite_file_dir_path

    @property
    def suite_file_dir_path(self) -> pathlib.Path:
        return self.__suite_file_dir_path


class TestCaseSectionInstruction(Instruction):
    def validate(self,
                 environment: Environment):
        raise NotImplementedError()

    def main(self,
             environment: Environment) -> list:
        """
        :return: List of TestCase
        """
        raise NotImplementedError()


class TestSuiteSectionInstruction(Instruction):
    def validate(self,
                 environment: Environment):
        raise NotImplementedError()

    def main(self,
             environment: Environment) -> TestSuite:
        raise NotImplementedError()