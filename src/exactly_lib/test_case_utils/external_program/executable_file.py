from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.test_case_utils.external_program.command.command_resolver import CommandResolver
from exactly_lib.test_case_utils.external_program.command.driver_resolvers import \
    CommandDriverResolverForExecutableFile
from exactly_lib.test_case_utils.external_program.validators import ExistingExecutableFileValidator


class ExecutableFileWithArgsResolver(CommandResolver):
    def __init__(self,
                 executable_file: FileRefResolver,
                 arguments: ListResolver):
        super().__init__(CommandDriverResolverForExecutableFile(executable_file),
                         arguments,
                         ExistingExecutableFileValidator(executable_file))
        self._executable_file = executable_file

    @property
    def executable_file(self) -> FileRefResolver:
        return self._executable_file
