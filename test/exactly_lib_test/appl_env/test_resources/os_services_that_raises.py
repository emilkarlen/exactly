import pathlib

from exactly_lib.appl_env.command_executor import CommandExecutor
from exactly_lib.appl_env.os_services import OsServices


class OsServicesThatRaises(OsServices):
    @property
    def command_executor(self) -> CommandExecutor:
        raise NotImplementedError('Should never be used')

    def make_dir_if_not_exists(self, path: pathlib.Path):
        raise NotImplementedError('Should never be used')

    def copy_file__preserve_as_much_as_possible(self, src: str, dst: str):
        raise NotImplementedError('Should never be used')

    def copy_file(self, src: pathlib.Path, dst: pathlib.Path):
        raise NotImplementedError('Should never be used')

    def copy_tree__preserve_as_much_as_possible(self, src: str, dst: str):
        raise NotImplementedError('Should never be used')
