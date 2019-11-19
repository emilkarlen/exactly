from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case_utils.program.command import command_sdvs


class ExecutableFileWithArgsResolver:
    def __init__(self,
                 executable_file: PathSdv,
                 arguments: ListSdv):
        self._executable_file = executable_file
        self._arguments = arguments

    @property
    def executable_file(self) -> PathSdv:
        return self._executable_file

    @property
    def arguments(self) -> ListSdv:
        return self._arguments

    @property
    def as_command(self) -> CommandSdv:
        return command_sdvs.for_executable_file(self.executable_file) \
            .new_with_additional_argument_list(self._arguments)
