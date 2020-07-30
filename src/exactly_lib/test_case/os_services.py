import pathlib
from abc import ABC, abstractmethod

from exactly_lib.test_case import exception_detection
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case.result import sh


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

    def copy_file_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        return exception_detection.return_success_or_hard_error(
            self.copy_file_preserve_as_much_as_possible__detect_ex,
            src, dst)

    def copy_tree_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        return exception_detection.return_success_or_hard_error(
            self.copy_tree_preserve_as_much_as_possible__detect_ex,
            src, dst)
