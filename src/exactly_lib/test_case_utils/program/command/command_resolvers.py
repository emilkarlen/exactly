from exactly_lib.symbol.data import list_resolvers, string_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.program import arguments_resolver
from exactly_lib.symbol.program.arguments_resolver import ArgumentsResolver
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.test_case_utils.program.command import driver_resolvers as drivers
from exactly_lib.util.process_execution.os_process_execution import ProgramAndArguments


def for_shell(arguments: ArgumentsResolver = arguments_resolver.no_arguments()) -> CommandResolver:
    return CommandResolver(drivers.CommandDriverResolverForShell(),
                           arguments)


def for_executable_file(executable_file: FileRefResolver,
                        arguments: ArgumentsResolver = arguments_resolver.no_arguments()) -> CommandResolver:
    return CommandResolver(
        drivers.CommandDriverResolverForExecutableFile(executable_file),
        arguments)


def for_system_program(program: StringResolver,
                       arguments: ArgumentsResolver = arguments_resolver.no_arguments()) -> CommandResolver:
    return CommandResolver(drivers.CommandDriverResolverForSystemProgram(program),
                           arguments)


def from_program_and_arguments(pgm_and_args: ProgramAndArguments) -> CommandResolver:
    program = string_resolvers.str_constant(pgm_and_args.program)
    arguments = list_resolvers.from_str_constants(pgm_and_args.arguments)
    additional_arguments = arguments_resolver.new_without_validation(arguments)
    return for_system_program(program).new_with_additional_arguments(additional_arguments)
