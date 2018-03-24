import sys

from exactly_lib.symbol.data.concrete_resolvers import list_constant
from exactly_lib.symbol.data.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.test_case_utils.sub_proc.command_resolvers import CmdAndArgsResolverForProgramAndArguments, \
    CmdAndArgsResolverForExecutableFile
from exactly_lib.test_case_utils.sub_proc.executable_file import ExecutableFileWithArgs
from exactly_lib.type_system.data import file_refs
from exactly_lib_test.test_resources.programs.python_program_execution import \
    PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE

EXECUTABLE_FILE_FOR_PY_SRC_AS_ONE_AND_ONLY_ARG = ExecutableFileWithArgs(
    FileRefConstant(file_refs.absolute_file_name(sys.executable)),
    list_constant([PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE]),
)


def command_resolver_for_source_on_command_line(python_source: str) -> CmdAndArgsResolverForProgramAndArguments:
    return CmdAndArgsResolverForExecutableFile(EXECUTABLE_FILE_FOR_PY_SRC_AS_ONE_AND_ONLY_ARG,
                                               list_constant([python_source]))
