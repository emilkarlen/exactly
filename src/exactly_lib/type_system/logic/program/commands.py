from typing import Sequence

from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.program.validators import ExistingExecutableFileValidator
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.logic.program.command import CommandDriverDdv
from exactly_lib.util.process_execution import commands
from exactly_lib.util.process_execution.command import CommandDriver


class CommandDriverDdvForShell(CommandDriverDdv):
    def __init__(self, command_line: StringDdv):
        self._command_line = command_line

    def value_of_any_dependency(self, tcds: Tcds) -> CommandDriver:
        return commands.CommandDriverForShell(self._command_line.value_of_any_dependency(tcds))


class CommandDriverDdvForExecutableFile(CommandDriverDdv):
    def __init__(self, exe_file: PathDdv):
        self._exe_file = exe_file
        self._validators = (ExistingExecutableFileValidator(exe_file),)

    @property
    def validators(self) -> Sequence[DdvValidator]:
        return self._validators

    def value_of_any_dependency(self, tcds: Tcds) -> CommandDriver:
        return commands.CommandDriverForExecutableFile(self._exe_file.value_of_any_dependency(tcds))


class CommandDriverDdvForSystemProgram(CommandDriverDdv):
    def __init__(self, program: StringDdv):
        self._program = program

    def value_of_any_dependency(self, tcds: Tcds) -> CommandDriver:
        return commands.CommandDriverForSystemProgram(self._program.value_of_any_dependency(tcds))
