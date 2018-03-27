from typing import Sequence

from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.external_program.command.command_resolver import CommandDriverResolver
from exactly_lib.util.process_execution import os_process_execution
from exactly_lib.util.process_execution.os_process_execution import Command


class CommandDriverResolverForExecutableFile(CommandDriverResolver):
    def __init__(self, executable_file: FileRefResolver):
        self._executable_file = executable_file

    @property
    def executable_file(self) -> FileRefResolver:
        return self._executable_file

    def resolve(self,
                environment: PathResolvingEnvironmentPreOrPostSds,
                arguments: ListResolver) -> Command:
        return os_process_execution.executable_file_command(
            self.executable_file.resolve_value_of_any_dependency(environment),
            arguments.resolve_value_of_any_dependency(environment)
        )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._executable_file.references


class CommandDriverResolverForSystemProgram(CommandDriverResolver):
    def __init__(self, program: StringResolver):
        self._program = program

    @property
    def program(self) -> StringResolver:
        return self._program

    def resolve(self,
                environment: PathResolvingEnvironmentPreOrPostSds,
                arguments: ListResolver) -> Command:
        return os_process_execution.executable_program_command(
            self._program.resolve_value_of_any_dependency(environment),
            arguments.resolve_value_of_any_dependency(environment)
        )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._program.references


class CommandDriverResolverForShell(CommandDriverResolver):
    def resolve(self,
                environment: PathResolvingEnvironmentPreOrPostSds,
                arguments: ListResolver) -> Command:
        arguments_as_string = string_resolvers.from_list_resolver(arguments)
        arguments_as_str = arguments_as_string.resolve_value_of_any_dependency(environment)
        return os_process_execution.shell_command(arguments_as_str)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()
