import pathlib
from abc import ABC, abstractmethod

from exactly_lib.test_case.command_executor import CommandExecutor


class OsServices(ABC):
    """
    Interface to some Operation System Services.

    These are services may vary depending on operating system.
    """

    @property
    @abstractmethod
    def command_executor(self) -> CommandExecutor:
        pass

    def make_dir_if_not_exists(self, path: pathlib.Path):
        """
        :raises HardErrorException
        """
        raise NotImplementedError()

    def copy_file__preserve_as_much_as_possible(self, src: str, dst: str):
        """
        :raises HardErrorException
        """
        raise NotImplementedError()

    def copy_file(self, src: pathlib.Path, dst: pathlib.Path):
        """
        :param src: A readable regular file.
        :param dst: Will be overwritten if it exists.
        :raises HardErrorException
        """
        raise NotImplementedError()

    def copy_tree__preserve_as_much_as_possible(self, src: str, dst: str):
        """
        :raises HardErrorException
        """
        raise NotImplementedError()
