import sys

from exactly_lib.symbol.data.list_resolver import from_str_constants
from exactly_lib.symbol.data.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.test_case_utils.sub_proc.command_resolvers import CommandResolverForExecutableFile
from exactly_lib.test_case_utils.sub_proc.executable_file import ExecutableFileWithArgs
from exactly_lib.type_system.data import file_refs
from exactly_lib_test.test_resources.programs.python_program_execution import \
    PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE

EXECUTABLE_FILE_FOR_PY_SRC_AS_ONE_AND_ONLY_ARG = ExecutableFileWithArgs(
    FileRefConstant(file_refs.absolute_file_name(sys.executable)),
    from_str_constants([PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE]),
)


def command_resolver_for_source_on_command_line(python_source: str) -> CommandResolverForExecutableFile:
    return CommandResolverForExecutableFile(EXECUTABLE_FILE_FOR_PY_SRC_AS_ONE_AND_ONLY_ARG,
                                            from_str_constants([python_source]))
