from typing import Sequence

from exactly_lib.symbol.data import list_resolvers, string_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.program.arguments_resolver import ArgumentsResolver
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.program.command import arguments_resolvers
from exactly_lib.test_case_utils.program.command import driver_resolvers as drivers
from exactly_lib.util.process_execution.command import ProgramAndArguments


def for_shell(command_line: StringResolver,
              arguments: ArgumentsResolver = arguments_resolvers.empty(),
              validators: Sequence[PreOrPostSdsValidator] = ()) -> CommandResolver:
    return CommandResolver(drivers.CommandDriverResolverForShell(command_line,
                                                                 validators),
                           arguments)


def for_executable_file(executable_file: FileRefResolver,
                        arguments: ArgumentsResolver = arguments_resolvers.empty()) -> CommandResolver:
    return CommandResolver(
        drivers.CommandDriverResolverForExecutableFile(executable_file),
        arguments)


def for_system_program(program: StringResolver,
                       arguments: ArgumentsResolver = arguments_resolvers.empty()) -> CommandResolver:
    return CommandResolver(drivers.CommandDriverResolverForSystemProgram(program),
                           arguments)


def from_program_and_arguments(pgm_and_args: ProgramAndArguments) -> CommandResolver:
    program = string_resolvers.str_constant(pgm_and_args.program)
    arguments = list_resolvers.from_str_constants(pgm_and_args.arguments)
    additional_arguments = arguments_resolvers.new_without_validation(arguments)
    return for_system_program(program).new_with_additional_arguments(additional_arguments)
