import pathlib
from abc import ABC, abstractmethod

from exactly_lib.appl_env.command_executor import CommandExecutor


class OsServices(ABC):
    """
    Interface to some Operation System Services.

    These are services may vary depending on operating system.
    """

    @property
    @abstractmethod
    def command_executor(self) -> CommandExecutor:
        pass

    def make_dir_if_not_exists__detect_ex(self, path: pathlib.Path):
        """
        :raises DetectedException
        """
        raise NotImplementedError()

    def copy_file_preserve_as_much_as_possible__detect_ex(self, src: str, dst: str):
        """
        :raises DetectedException
        """
        raise NotImplementedError()

    def copy_file__detect_ex(self, src: pathlib.Path, dst: pathlib.Path):
        """
        :param src: A readable regular file.
        :param dst: Will be overwritten if it exists.
        :raises DetectedException
        """
        raise NotImplementedError()

    def copy_tree_preserve_as_much_as_possible__detect_ex(self, src: str, dst: str):
        """
        :raises DetectedException
        """
        raise NotImplementedError()
