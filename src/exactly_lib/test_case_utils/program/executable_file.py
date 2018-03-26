import pathlib
import stat

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.test_case_utils.file_ref_validator import FileRefValidatorBase
from exactly_lib.test_case_utils.program.command.new_command_resolver import NewCommandResolver
from exactly_lib.test_case_utils.program.command.new_driver_resolvers import \
    NewCommandDriverResolverForExecutableFile


class NewCommandResolverForExecutableFileWip(NewCommandResolver):
    def __init__(self,
                 executable_file: FileRefResolver,
                 arguments: ListResolver):
        super().__init__(NewCommandDriverResolverForExecutableFile(executable_file),
                         arguments,
                         ExistingExecutableFileValidator(executable_file))
        self._executable_file = executable_file

    @property
    def executable_file(self) -> FileRefResolver:
        return self._executable_file


class ExistingExecutableFileValidator(FileRefValidatorBase):
    def _validate_path(self, file_path: pathlib.Path) -> str:
        if not file_path.is_file():
            return 'File does not exist: {}'.format(file_path)
        stat_value = file_path.stat()
        mode = stat_value.st_mode
        if not mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            return 'File is not executable. Mode is {}: {}'.format(stat.filemode(mode), file_path)
        return None
