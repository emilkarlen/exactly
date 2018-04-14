from typing import Set

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.logic.program.command_value import CommandDriverValue
from exactly_lib.util.process_execution import commands
from exactly_lib.util.process_execution.command import CommandDriver


class CommandDriverValueForShell(CommandDriverValue):
    def __init__(self, command_line: StringValue):
        self._command_line = command_line

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._command_line.resolving_dependencies()

    def value_when_no_dir_dependencies(self) -> CommandDriver:
        return commands.CommandDriverForShell(self._command_line.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> CommandDriver:
        return commands.CommandDriverForShell(self._command_line.value_of_any_dependency(home_and_sds))


class CommandDriverValueForExecutableFile(CommandDriverValue):
    def __init__(self, exe_file: FileRef):
        self._exe_file = exe_file

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._exe_file.resolving_dependencies()

    def value_when_no_dir_dependencies(self) -> CommandDriver:
        return commands.CommandDriverForExecutableFile(self._exe_file.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> CommandDriver:
        return commands.CommandDriverForExecutableFile(self._exe_file.value_of_any_dependency(home_and_sds))


class CommandDriverValueForSystemProgram(CommandDriverValue):
    def __init__(self, program: StringValue):
        self._program = program

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._program.resolving_dependencies()

    def value_when_no_dir_dependencies(self) -> CommandDriver:
        return commands.CommandDriverForSystemProgram(self._program.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> CommandDriver:
        return commands.CommandDriverForSystemProgram(self._program.value_of_any_dependency(home_and_sds))
