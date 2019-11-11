from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.logic.program.command_value import CommandDriverValue
from exactly_lib.util.process_execution import commands
from exactly_lib.util.process_execution.command import CommandDriver


class CommandDriverValueForShell(CommandDriverValue):
    def __init__(self, command_line: StringValue):
        self._command_line = command_line

    def value_of_any_dependency(self, tcds: HomeAndSds) -> CommandDriver:
        return commands.CommandDriverForShell(self._command_line.value_of_any_dependency(tcds))


class CommandDriverValueForExecutableFile(CommandDriverValue):
    def __init__(self, exe_file: FileRef):
        self._exe_file = exe_file

    def value_of_any_dependency(self, tcds: HomeAndSds) -> CommandDriver:
        return commands.CommandDriverForExecutableFile(self._exe_file.value_of_any_dependency(tcds))


class CommandDriverValueForSystemProgram(CommandDriverValue):
    def __init__(self, program: StringValue):
        self._program = program

    def value_of_any_dependency(self, tcds: HomeAndSds) -> CommandDriver:
        return commands.CommandDriverForSystemProgram(self._program.value_of_any_dependency(tcds))
