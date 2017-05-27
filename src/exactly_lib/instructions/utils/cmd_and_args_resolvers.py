from exactly_lib.instructions.utils.executable_file import ExecutableFile
from exactly_lib.instructions.utils.sub_process_execution import CmdAndArgsResolver
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds


class ConstantCmdAndArgsResolver(CmdAndArgsResolver):
    def __init__(self, cmd_or_cmd_and_args):
        """
        :param cmd_or_cmd_and_args: Either a string or a list of strings
        """
        self.__cmd_or_cmd_and_args = cmd_or_cmd_and_args

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds):
        return self.__cmd_or_cmd_and_args


class CmdAndArgsResolverForExecutableFileBase(CmdAndArgsResolver):
    def __init__(self, executable: ExecutableFile):
        self.__executable = executable

    @property
    def symbol_usages(self) -> list:
        return self.__executable.symbol_usages

    def _arguments(self, environment: PathResolvingEnvironmentPreOrPostSds) -> list:
        raise NotImplementedError()

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> list:
        return [self.__executable.path_string(environment)] + \
               self.__executable.arguments + \
               self._arguments(environment)
