from exactly_lib.test_case_utils.program.command import arguments_sdvs
from exactly_lib.test_case_utils.program.command import driver_sdvs as drivers
from exactly_lib.type_system.logic.program.command import ProgramAndArguments
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib.type_val_deps.types.string import string_sdvs
from exactly_lib.type_val_deps.types.string.string_sdv import StringSdv


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
