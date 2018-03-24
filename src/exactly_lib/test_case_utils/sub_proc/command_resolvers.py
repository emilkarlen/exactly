from typing import List, Sequence

from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.sub_proc.executable_file import ExecutableFileAndArgs
from exactly_lib.test_case_utils.sub_proc.sub_process_execution import CmdAndArgsResolver


class CmdAndArgsResolverForProgramAndArguments(CmdAndArgsResolver):
    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds):
        return self.resolve_program_and_arguments(environment)

    def resolve_program_and_arguments(self, environment: PathResolvingEnvironmentPreOrPostSds) -> List[str]:
        raise NotImplementedError('abstract method')


class CmdAndArgsResolverForShell(CmdAndArgsResolver):
    def __init__(self, cmd_resolver: StringResolver):
        self.__cmd_resolver = cmd_resolver

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        value = self.__cmd_resolver.resolve(environment.symbols)
        return value.value_of_any_dependency(environment.home_and_sds)

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return self.__cmd_resolver.references


class CmdAndArgsResolverForExecutableFile(CmdAndArgsResolverForProgramAndArguments):
    def __init__(self, executable: ExecutableFileAndArgs):
        self.__executable = executable

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return self.__executable.symbol_usages

    def _additional_arguments(self, environment: PathResolvingEnvironmentPreOrPostSds) -> List[str]:
        return []

    def resolve_program_and_arguments(self, environment: PathResolvingEnvironmentPreOrPostSds) -> List[str]:
        arguments_list_value = self.__executable.arguments.resolve(environment.symbols)
        argument_strings = arguments_list_value.value_of_any_dependency(environment.home_and_sds)
        return ([self.__executable.path_string(environment)] +
                argument_strings +
                self._additional_arguments(environment)
                )
