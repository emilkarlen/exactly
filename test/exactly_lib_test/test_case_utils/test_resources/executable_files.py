import sys

from exactly_lib.symbol.data import list_resolvers, file_ref_resolvers2
from exactly_lib.test_case_utils.external_program.command import command_resolvers
from exactly_lib.test_case_utils.external_program.command.command_resolver import CommandResolver
from exactly_lib.type_system.data import file_refs
from exactly_lib_test.test_resources.programs.python_program_execution import \
    PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE

EXECUTABLE_FILE_FOR_PY_SRC_AS_ONE_AND_ONLY_ARG = command_resolvers.for_executable_file(
    file_ref_resolvers2.constant(file_refs.absolute_file_name(sys.executable))
).new_with_additional_arguments(list_resolvers.from_str_constants([PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE]))


def command_resolver_for_source_on_command_line(python_source: str) -> CommandResolver:
    return EXECUTABLE_FILE_FOR_PY_SRC_AS_ONE_AND_ONLY_ARG.new_with_additional_arguments(
        list_resolvers.from_str_constant(python_source))
