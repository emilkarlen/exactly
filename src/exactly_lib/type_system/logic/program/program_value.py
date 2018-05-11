from typing import Set

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic.program.command_value import CommandValue
from exactly_lib.type_system.logic.program.stdin_data_values import StdinDataValue, StdinData
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerValue
from exactly_lib.type_system.utils import resolving_dependencies_from_sequence
from exactly_lib.util.process_execution.command import Command


class Program(tuple):
    def __new__(cls,
                command: Command,
                stdin: StdinData,
                transformation: StringTransformer):
        return tuple.__new__(cls, (command, stdin, transformation))

    @property
    def command(self) -> Command:
        return self[0]

    @property
    def stdin(self) -> StdinData:
        return self[1]

    @property
    def transformation(self) -> StringTransformer:
        return self[2]


class ProgramValue(MultiDirDependentValue[Program]):
    def __init__(self,
                 command: CommandValue,
                 stdin: StdinDataValue,
                 transformation: StringTransformerValue):
        self._command = command
        self._stdin = stdin
        self._transformation = transformation

    @property
    def command(self) -> CommandValue:
        return self._command

    @property
    def stdin(self) -> StdinDataValue:
        return self._stdin

    @property
    def transformation(self) -> StringTransformerValue:
        return self._transformation

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return resolving_dependencies_from_sequence([self.command,
                                                     self.stdin,
                                                     self.transformation])

    def value_when_no_dir_dependencies(self) -> Program:
        return Program(self.command.value_when_no_dir_dependencies(),
                       self.stdin.value_when_no_dir_dependencies(),
                       self.transformation.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> Program:
        return Program(self.command.value_of_any_dependency(home_and_sds),
                       self.stdin.value_of_any_dependency(home_and_sds),
                       self.transformation.value_of_any_dependency(home_and_sds))
