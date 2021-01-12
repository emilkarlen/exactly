import sys

from exactly_lib.impls.types.program.command import arguments_sdvs
from exactly_lib.impls.types.program.command import driver_sdvs as drivers
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib_test.test_resources.programs.python_program_execution import \
    PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE

PYTHON_EXECUTABLE_DRIVER = drivers.CommandDriverSdvForExecutableFile(
    path_sdvs.constant(path_ddvs.absolute_file_name(sys.executable)))

PYTHON_EXECUTABLE_COMMAND = CommandSdv(PYTHON_EXECUTABLE_DRIVER,
                                       ArgumentsSdv.empty())

EXECUTABLE_FILE_FOR_PY_SRC_ON_COMMAND_LINE = PYTHON_EXECUTABLE_COMMAND.new_with_additional_argument_list(
    list_sdvs.from_str_constant(PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE))


def for_py_source_on_command_line(python_source: str) -> CommandSdv:
    return EXECUTABLE_FILE_FOR_PY_SRC_ON_COMMAND_LINE.new_with_additional_argument_list(
        list_sdvs.from_str_constant(python_source))


def for_interpret_py_file_that_must_exist(python_source_file: PathSdv) -> CommandSdv:
    return PYTHON_EXECUTABLE_COMMAND.new_with_additional_arguments(
        arguments_sdvs.ref_to_file_that_must_exist(python_source_file))
