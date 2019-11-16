from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.logic.program.command_value import CommandDriverValue
from exactly_lib.util.process_execution import commands
from exactly_lib.util.process_execution.command import CommandDriver


class CommandDriverValueForShell(CommandDriverValue):
    def __init__(self, command_line: StringDdv):
        self._command_line = command_line

    def value_of_any_dependency(self, tcds: Tcds) -> CommandDriver:
        return commands.CommandDriverForShell(self._command_line.value_of_any_dependency(tcds))


class CommandDriverValueForExecutableFile(CommandDriverValue):
    def __init__(self, exe_file: PathDdv):
        self._exe_file = exe_file

    def value_of_any_dependency(self, tcds: Tcds) -> CommandDriver:
        return commands.CommandDriverForExecutableFile(self._exe_file.value_of_any_dependency(tcds))


class CommandDriverValueForSystemProgram(CommandDriverValue):
    def __init__(self, program: StringDdv):
        self._program = program

    def value_of_any_dependency(self, tcds: Tcds) -> CommandDriver:
        return commands.CommandDriverForSystemProgram(self._program.value_of_any_dependency(tcds))
