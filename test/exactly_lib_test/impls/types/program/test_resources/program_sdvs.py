from exactly_lib.impls.types.program.command import command_sdvs
from exactly_lib.impls.types.program.sdvs import command_program_sdv
from exactly_lib.impls.types.program.sdvs.command_program_sdv import ProgramSdvForCommand
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib_test.impls.types.test_resources import command_sdvs as test_command_sdvs
from exactly_lib_test.type_val_deps.types.string.test_resources import string_sdvs


def arbitrary() -> ProgramSdv:
    return arbitrary__without_symbol_references()


def arbitrary__without_symbol_references() -> ProgramSdv:
    return system_program(
        string_sdvs.StringSdvTestImpl('system-program'))


def ref_to_exe_file(exe_file: PathSdv,
                    arguments: ArgumentsSdv = ArgumentsSdv.empty()
                    ) -> ProgramSdvForCommand:
    return command_program_sdv.plain(
        command_sdvs.for_executable_file(exe_file, arguments)
    )


def system_program(program: StringSdv,
                   arguments: ArgumentsSdv = ArgumentsSdv.empty()
                   ) -> ProgramSdvForCommand:
    return command_program_sdv.plain(
        command_sdvs.for_system_program(program, arguments)
    )


def interpret_py_source_file_that_must_exist(py_source_file: PathSdv,
                                             arguments: ArgumentsSdv = ArgumentsSdv.empty()
                                             ) -> ProgramSdvForCommand:
    return command_program_sdv.plain(
        test_command_sdvs.for_interpret_py_file_that_must_exist(py_source_file)
    ).new_accumulated(AccumulatedComponents.of_arguments(arguments))


def for_py_source_on_command_line(python_source: str) -> ProgramSdvForCommand:
    return command_program_sdv.plain(
        test_command_sdvs.for_py_source_on_command_line(python_source))
