import sys

from exactly_lib.symbol.data import list_resolvers, file_ref_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.logic.program.command_resolver import CommandResolver
from exactly_lib.test_case_utils.program.command import arguments_resolvers
from exactly_lib.test_case_utils.program.command import driver_resolvers as drivers
from exactly_lib.type_system.data import file_refs
from exactly_lib_test.test_resources.programs.python_program_execution import \
    PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE

PYTHON_EXECUTABLE_DRIVER = drivers.CommandDriverResolverForExecutableFile(
    file_ref_resolvers.constant(file_refs.absolute_file_name(sys.executable)))

PYTHON_EXECUTABLE_COMMAND = CommandResolver(PYTHON_EXECUTABLE_DRIVER,
                                            arguments_resolvers.empty())

EXECUTABLE_FILE_FOR_PY_SRC_ON_COMMAND_LINE = PYTHON_EXECUTABLE_COMMAND.new_with_additional_argument_list(
    list_resolvers.from_str_constant(PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE))


def for_py_source_on_command_line(python_source: str) -> CommandResolver:
    return EXECUTABLE_FILE_FOR_PY_SRC_ON_COMMAND_LINE.new_with_additional_argument_list(
        list_resolvers.from_str_constant(python_source))


def for_interpret_py_file_that_must_exist(python_source_file: FileRefResolver) -> CommandResolver:
    return PYTHON_EXECUTABLE_COMMAND.new_with_additional_arguments(
        arguments_resolvers.ref_to_file_that_must_exist(python_source_file))
