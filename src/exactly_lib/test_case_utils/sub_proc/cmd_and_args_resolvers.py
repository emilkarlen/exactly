from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.resolver_structure import DataValueResolver
from exactly_lib.test_case_utils.sub_proc.executable_file import ExecutableFile
from exactly_lib.test_case_utils.sub_proc.sub_process_execution import CmdAndArgsResolver


class ConstantCmdAndArgsResolver(CmdAndArgsResolver):
    def __init__(self, cmd_or_cmd_and_args_resolver: DataValueResolver):
        """
        :param cmd_or_cmd_and_args: Either a string or a list of strings
        """
        self.__cmd_or_cmd_and_args_resolver = cmd_or_cmd_and_args_resolver

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds):
        value = self.__cmd_or_cmd_and_args_resolver.resolve(environment.symbols)
        return value.value_of_any_dependency(environment.home_and_sds)

    @property
    def symbol_usages(self) -> list:
        return self.__cmd_or_cmd_and_args_resolver.references


class CmdAndArgsResolverForExecutableFileBase(CmdAndArgsResolver):
    def __init__(self, executable: ExecutableFile):
        self.__executable = executable

    @property
    def symbol_usages(self) -> list:
        return self.__executable.symbol_usages

    def _arguments(self, environment: PathResolvingEnvironmentPreOrPostSds) -> list:
        raise NotImplementedError()

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> list:
        arguments_list_value = self.__executable.arguments.resolve(environment.symbols)
        argument_strings = arguments_list_value.value_of_any_dependency(environment.home_and_sds)
        return [self.__executable.path_string(environment)] + \
               argument_strings + \
               self._arguments(environment)
