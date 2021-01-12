from exactly_lib.impls.types.program.command import driver_sdvs as drivers
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_prims.program.command import ProgramAndArguments


def for_shell(command_line: StringSdv,
              arguments: ArgumentsSdv = ArgumentsSdv.empty()) -> CommandSdv:
    return CommandSdv(drivers.CommandDriverSdvForShell(command_line),
                      arguments)


def for_executable_file(executable_file: PathSdv,
                        arguments: ArgumentsSdv = ArgumentsSdv.empty()) -> CommandSdv:
    return CommandSdv(
        drivers.CommandDriverSdvForExecutableFile(executable_file),
        arguments)


def for_system_program(program: StringSdv,
                       arguments: ArgumentsSdv = ArgumentsSdv.empty()) -> CommandSdv:
    return CommandSdv(drivers.CommandDriverSdvForSystemProgram(program),
                      arguments)


def for_system_program__from_pgm_and_args(pgm_and_args: ProgramAndArguments) -> CommandSdv:
    program = string_sdvs.str_constant(pgm_and_args.program)
    arguments = list_sdvs.from_str_constants(pgm_and_args.arguments)
    additional_arguments = ArgumentsSdv.new_without_validation(arguments)
    return for_system_program(program).new_with_additional_arguments(additional_arguments)
