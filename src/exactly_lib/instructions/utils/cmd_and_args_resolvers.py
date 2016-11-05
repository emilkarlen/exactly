from exactly_lib.instructions.utils.executable_file import ExecutableFile
from exactly_lib.instructions.utils.sub_process_execution import CmdAndArgsResolver
from exactly_lib.test_case.phases.common import HomeAndSds


class ConstantCmdAndArgsResolver(CmdAndArgsResolver):
    def __init__(self, cmd_or_cmd_and_args):
        """
        :param cmd_or_cmd_and_args: Either a string or a list of strings
        """
        self.__cmd_or_cmd_and_args = cmd_or_cmd_and_args

    def resolve(self, home_and_sds: HomeAndSds):
        return self.__cmd_or_cmd_and_args


class CmdAndArgsResolverForExecutableFileBase(CmdAndArgsResolver):
    def __init__(self, executable: ExecutableFile):
        self.__executable = executable

    def _arguments(self, home_and_sds: HomeAndSds) -> list:
        raise NotImplementedError()

    def resolve(self, home_and_sds: HomeAndSds) -> list:
        return [self.__executable.path_string(home_and_sds)] + \
               self.__executable.arguments + \
               self._arguments(home_and_sds)
