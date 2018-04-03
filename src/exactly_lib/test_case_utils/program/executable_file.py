from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.test_case_utils.program.command import command_resolvers


class ExecutableFileWithArgsResolver:
    def __init__(self,
                 executable_file: FileRefResolver,
                 arguments: ListResolver):
        self._executable_file = executable_file
        self._arguments = arguments

    @property
    def executable_file(self) -> FileRefResolver:
        return self._executable_file

    @property
    def arguments(self) -> ListResolver:
        return self._arguments

    @property
    def as_command(self) -> CommandResolver:
        return command_resolvers.for_executable_file(self.executable_file) \
            .new_with_additional_argument_list(self._arguments)
