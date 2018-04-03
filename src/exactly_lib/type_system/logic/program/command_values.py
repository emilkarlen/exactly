from typing import Set

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.logic.program.command_value import CommandValue
from exactly_lib.util.process_execution.os_process_execution import Command, ShellCommand, ExecutableFileCommand, \
    ExecutableProgramCommand, ProgramAndArguments


class CommandValueForShell(CommandValue):
    def __init__(self, command_line: StringValue):
        self._command_line = command_line

    def resolving_dependencies(self) -> Set[ResolvingDependency]:
        return self._command_line.resolving_dependencies()

    def value_when_no_dir_dependencies(self) -> Command:
        return ShellCommand(self._command_line.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> Command:
        return ShellCommand(self._command_line.value_of_any_dependency(home_and_sds))


class CommandValueForExecutableFile(CommandValue):
    def __init__(self,
                 exe_file: FileRef,
                 arguments: ListValue):
        self._exe_file = exe_file
        self._arguments = arguments

    def resolving_dependencies(self) -> Set[ResolvingDependency]:
        return self._exe_file.resolving_dependencies().union(self._arguments.resolving_dependencies())

    def value_when_no_dir_dependencies(self) -> Command:
        return ExecutableFileCommand(self._exe_file.value_when_no_dir_dependencies(),
                                     self._arguments.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> Command:
        return ExecutableFileCommand(self._exe_file.value_of_any_dependency(home_and_sds),
                                     self._arguments.value_of_any_dependency(home_and_sds))


class CommandValueForSystemProgram(CommandValue):
    def __init__(self,
                 program: StringValue,
                 arguments: ListValue):
        self._program = program
        self._arguments = arguments

    def resolving_dependencies(self) -> Set[ResolvingDependency]:
        return self._program.resolving_dependencies().union(self._arguments.resolving_dependencies())

    def value_when_no_dir_dependencies(self) -> Command:
        return self._of(ProgramAndArguments(self._program.value_when_no_dir_dependencies(),
                                            self._arguments.value_when_no_dir_dependencies()))

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> Command:
        return self._of(ProgramAndArguments(self._program.value_of_any_dependency(home_and_sds),
                                            self._arguments.value_of_any_dependency(home_and_sds)))

    @staticmethod
    def _of(pgm_and_args: ProgramAndArguments) -> Command:
        return ExecutableProgramCommand(pgm_and_args)
