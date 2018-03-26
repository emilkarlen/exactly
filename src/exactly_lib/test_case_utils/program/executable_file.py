from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.test_case_utils.program.command.new_command_resolver import NewCommandResolver
from exactly_lib.test_case_utils.program.command.new_driver_resolvers import \
    NewCommandDriverResolverForExecutableFile
from exactly_lib.test_case_utils.program.validators import ExistingExecutableFileValidator


class ExecutableFileWithArgsResolver(NewCommandResolver):
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
