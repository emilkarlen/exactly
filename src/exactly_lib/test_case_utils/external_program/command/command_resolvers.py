from exactly_lib.symbol.data import list_resolvers, string_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.test_case_utils.external_program.command import driver_resolvers as drivers
from exactly_lib.test_case_utils.external_program.command.command_resolver import CommandResolver, ArgumentsResolver
from exactly_lib.test_case_utils.external_program.validators import ExistingExecutableFileValidator
from exactly_lib.util.process_execution.os_process_execution import ProgramAndArguments


def for_shell() -> CommandResolver:
    return CommandResolver(drivers.CommandDriverResolverForShell(),
                           ArgumentsResolver(list_resolvers.empty()))


def for_executable_file(executable_file: FileRefResolver) -> CommandResolver:
    return CommandResolver(
        drivers.CommandDriverResolverForExecutableFile(executable_file,
                                                       [ExistingExecutableFileValidator(executable_file)]),
        ArgumentsResolver(list_resolvers.empty()))


def for_system_program(program: StringResolver) -> CommandResolver:
    return CommandResolver(drivers.CommandDriverResolverForSystemProgram(program),
                           ArgumentsResolver(list_resolvers.empty()))


def from_program_and_arguments(pgm_and_args: ProgramAndArguments) -> CommandResolver:
    program_resolver = string_resolvers.str_constant(pgm_and_args.program)
    arguments_resolver = list_resolvers.from_str_constants(pgm_and_args.arguments)
    return for_system_program(program_resolver).new_with_additional_arguments(arguments_resolver)
