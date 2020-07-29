import pathlib

from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.result import sh


class OsServicesThatRaises(OsServices):
    def command_executor(self) -> CommandExecutor:
        raise NotImplementedError('Should never be used')

    def make_dir_if_not_exists__detect_ex(self, path: pathlib.Path):
        raise NotImplementedError('Should never be used')

    def copy_file_preserve_as_much_as_possible__detect_ex(self, src: str, dst: str):
        raise NotImplementedError('Should never be used')

    def copy_file__detect_ex(self, src: pathlib.Path, dst: pathlib.Path):
        raise NotImplementedError('Should never be used')

    def copy_tree_preserve_as_much_as_possible__detect_ex(self, src: str, dst: str):
        raise NotImplementedError('Should never be used')

    def copy_file_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        raise NotImplementedError('Should never be used')

    def copy_tree_preserve_as_much_as_possible(self, src: str, dst: str) -> sh.SuccessOrHardError:
        raise NotImplementedError('Should never be used')
