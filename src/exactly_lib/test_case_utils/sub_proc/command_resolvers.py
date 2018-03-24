from typing import List, Sequence

from exactly_lib.symbol.data import list_resolver
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


class CommandResolverForProgramAndArguments(CommandResolver):
    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds):
        return self.resolve_program_and_arguments(environment)

    def resolve_program_and_arguments(self, environment: PathResolvingEnvironmentPreOrPostSds) -> List[str]:
        raise NotImplementedError('abstract method')


class CommandResolverForShell(CommandResolver):
    def __init__(self, cmd_resolver: StringResolver):
        self.__cmd_resolver = cmd_resolver

    def resolve_command(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        return os_process_execution.shell_command(self.resolve(environment))

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        value = self.__cmd_resolver.resolve(environment.symbols)
        return value.value_of_any_dependency(environment.home_and_sds)

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return self.__cmd_resolver.references


class CommandResolverForExecutableFileAndArguments(CommandResolverForProgramAndArguments):
    def resolve_command(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        return os_process_execution.executable_program_command(self.resolve(environment))

    @property
    def executable_file(self) -> FileRefResolver:
        raise NotImplementedError('abstract method')

    @property
    def arguments(self) -> ListResolver:
        raise NotImplementedError('abstract method')

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([self.executable_file, self.arguments])

    def resolve_program_and_arguments(self, environment: PathResolvingEnvironmentPreOrPostSds) -> List[str]:
        argument_strings = self.arguments.resolve_value_of_any_dependency(environment)
        executable_file_path = self.executable_file.resolve_value_of_any_dependency(environment)
        return [str(executable_file_path)] + argument_strings


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
