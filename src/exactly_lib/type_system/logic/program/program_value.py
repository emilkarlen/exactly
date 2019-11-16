from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.program.command_value import CommandValue
from exactly_lib.type_system.logic.program.stdin_data_values import StdinDataValue, StdinData
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv
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


class ProgramValue(DirDependentValue[Program]):
    def __init__(self,
                 command: CommandValue,
                 stdin: StdinDataValue,
                 transformation: StringTransformerDdv):
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
    def transformation(self) -> StringTransformerDdv:
        return self._transformation

    def value_of_any_dependency(self, tcds: Tcds) -> Program:
        return Program(self.command.value_of_any_dependency(tcds),
                       self.stdin.value_of_any_dependency(tcds),
                       self.transformation.value_of_any_dependency(tcds))
