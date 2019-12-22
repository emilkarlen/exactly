from exactly_lib.symbol.data import list_sdvs, string_sdvs
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.logic.program.arguments_sdv import ArgumentsSdv
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case_utils.program.command import arguments_sdvs
from exactly_lib.test_case_utils.program.command import driver_sdvs as drivers
from exactly_lib.type_system.logic.program.process_execution.command import ProgramAndArguments


def for_shell(command_line: StringSdv,
              arguments: ArgumentsSdv = arguments_sdvs.empty()) -> CommandSdv:
    return CommandSdv(drivers.CommandDriverSdvForShell(command_line),
                      arguments)


def for_executable_file(executable_file: PathSdv,
                        arguments: ArgumentsSdv = arguments_sdvs.empty()) -> CommandSdv:
    return CommandSdv(
        drivers.CommandDriverSdvForExecutableFile(executable_file),
        arguments)


def for_system_program(program: StringSdv,
                       arguments: ArgumentsSdv = arguments_sdvs.empty()) -> CommandSdv:
    return CommandSdv(drivers.CommandDriverSdvForSystemProgram(program),
                      arguments)


def for_system_program__from_pgm_and_args(pgm_and_args: ProgramAndArguments) -> CommandSdv:
    program = string_sdvs.str_constant(pgm_and_args.program)
    arguments = list_sdvs.from_str_constants(pgm_and_args.arguments)
    additional_arguments = arguments_sdvs.new_without_validation(arguments)
    return for_system_program(program).new_with_additional_arguments(additional_arguments)
