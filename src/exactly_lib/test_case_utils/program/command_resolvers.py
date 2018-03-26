from typing import Sequence

from exactly_lib.symbol.data import list_resolvers
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.program.command_resolver import CommandResolver
from exactly_lib.test_case_utils.program.executable_file import NewCommandResolverForExecutableFileWip
from exactly_lib.test_case_utils.program.program_with_args import ProgramWithArgsResolver
from exactly_lib.util.process_execution import os_process_execution
from exactly_lib.util.process_execution.os_process_execution import Command


class CommandResolverForShell(CommandResolver):
    def __init__(self, cmd_line_argument_as_list: ListResolver):
        super().__init__(cmd_line_argument_as_list)

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        return os_process_execution.shell_command(self._resolve_args(environment))

    def _resolve_args(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        string_arg = string_resolvers.from_list_resolver(self.arguments)
        return string_arg.resolve_value_of_any_dependency(environment)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.arguments.references


class CommandResolverForProgramAndArguments(CommandResolver):
    """
    A resolver that gives a command that is an executable file followed by a list arguments

    (opposed to a shell command which is just a string).
    """

    def __init__(self,
                 program: ProgramWithArgsResolver,
                 additional_arguments: ListResolver):
        super().__init__(list_resolvers.concat([program.arguments, additional_arguments]))
        self.__program_with_args = program
        self.__additional_arguments = additional_arguments

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        return os_process_execution.executable_program_command(
            self.__program_with_args.program.resolve_value_of_any_dependency(environment),
            self.arguments.resolve_value_of_any_dependency(environment)
        )

    @property
    def program(self) -> StringResolver:
        return self.__program_with_args.program

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([self.__program_with_args,
                                                               self.__additional_arguments])


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
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([self.executable_file, self.arguments])


class CommandResolverForExecutableFile(CommandResolverForExecutableFileAndArguments):
    def __init__(self,
                 executable: NewCommandResolverForExecutableFileWip,
                 additional_arguments: ListResolver):
        super().__init__(list_resolvers.concat([executable.arguments, additional_arguments]))
        self.__executable = executable
        self.__additional_arguments = additional_arguments

    @property
    def executable_file(self) -> FileRefResolver:
        return self.__executable.executable_file


def command_resolver_for_interpret(interpreter: NewCommandResolverForExecutableFileWip,
                                   file_to_interpret: FileRefResolver,
                                   argument_list: ListResolver) -> CommandResolverForExecutableFile:
    return CommandResolverForExecutableFile(interpreter,
                                            _file_interpreter_arguments(file_to_interpret,
                                                                        argument_list))


def command_resolver_for_interpret_by_program(interpreter: ProgramWithArgsResolver,
                                              file_to_interpret: FileRefResolver,
                                              argument_list: ListResolver) -> CommandResolverForProgramAndArguments:
    return CommandResolverForProgramAndArguments(interpreter,
                                                 _file_interpreter_arguments(file_to_interpret,
                                                                             argument_list))


def command_resolver_for_source_as_command_line_argument(interpreter: NewCommandResolverForExecutableFileWip,
                                                         source: StringResolver) -> CommandResolverForExecutableFile:
    additional_arguments = list_resolvers.from_strings([source])
    return CommandResolverForExecutableFile(interpreter, additional_arguments)


def _file_interpreter_arguments(file_to_interpret: FileRefResolver,
                                argument_list: ListResolver) -> ListResolver:
    file_to_interpret_as_string = string_resolvers.from_file_ref_resolver(file_to_interpret)
    return list_resolvers.concat([
        list_resolvers.from_strings([file_to_interpret_as_string]),
        argument_list,
    ])
