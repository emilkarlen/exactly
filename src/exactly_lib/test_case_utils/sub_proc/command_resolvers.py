from typing import Sequence

from exactly_lib.symbol.data import list_resolver, concrete_string_resolvers
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.sub_proc.executable_file import ExecutableFileWithArgs
from exactly_lib.test_case_utils.sub_proc.sub_process_execution import CommandResolver
from exactly_lib.util.process_execution import os_process_execution
from exactly_lib.util.process_execution.os_process_execution import Command


class CommandResolverForShell(CommandResolver):
    def __init__(self, cmd_resolver: StringResolver):
        self.__cmd_resolver = cmd_resolver

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        return os_process_execution.shell_command(self._resolve_args(environment))

    def _resolve_args(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        value = self.__cmd_resolver.resolve(environment.symbols)
        return value.value_of_any_dependency(environment.home_and_sds)

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return self.__cmd_resolver.references


class CommandResolverForExecutableFileAndArguments(CommandResolver):
    """
    A resolver that gives a command that is an executable file followed by a list arguments

    (opposed to a shell command which is just a string).
    """

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        return os_process_execution.executable_file_command(
            self.executable_file.resolve_value_of_any_dependency(environment),
            self.arguments.resolve_value_of_any_dependency(environment)
        )

    @property
    def executable_file(self) -> FileRefResolver:
        raise NotImplementedError('abstract method')

    @property
    def arguments(self) -> ListResolver:
        raise NotImplementedError('abstract method')

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([self.executable_file, self.arguments])


class CommandResolverForExecutableFile(CommandResolverForExecutableFileAndArguments):
    def __init__(self,
                 executable: ExecutableFileWithArgs,
                 additional_arguments: ListResolver):
        self.__executable = executable
        self.__additional_arguments = additional_arguments

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return tuple(self.__executable.symbol_usages) + tuple(self.__additional_arguments.references)

    @property
    def executable_file(self) -> FileRefResolver:
        return self.__executable.file_resolver

    @property
    def arguments(self) -> ListResolver:
        return list_resolver.concat_lists([self.__executable.arguments,
                                           self.__additional_arguments])


def command_resolver_for_interpret(interpreter: ExecutableFileWithArgs,
                                   file_to_interpret: FileRefResolver,
                                   argument_list: ListResolver) -> CommandResolverForExecutableFile:
    file_to_interpret_as_string = concrete_string_resolvers.from_file_ref_resolver(file_to_interpret)
    additional_arguments = list_resolver.concat_lists([
        list_resolver.from_strings([file_to_interpret_as_string]),
        argument_list,
    ])
    return CommandResolverForExecutableFile(interpreter, additional_arguments)


def command_resolver_for_source_as_command_line_argument(interpreter: ExecutableFileWithArgs,
                                                         source: StringResolver) -> CommandResolverForExecutableFile:
    additional_arguments = list_resolver.from_strings([source])
    return CommandResolverForExecutableFile(interpreter, additional_arguments)
