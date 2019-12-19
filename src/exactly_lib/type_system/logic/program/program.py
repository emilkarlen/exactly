from typing import Sequence

from exactly_lib.test_case.validation import ddv_validators
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, ApplicationEnvironment
from exactly_lib.type_system.logic.program.command import CommandDdv
from exactly_lib.type_system.logic.program.stdin_data import StdinDataDdv, StdinData
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


class ProgramAdv(ApplicationEnvironmentDependentValue[Program]):
    def __init__(self,
                 command: Command,
                 stdin: StdinData,
                 transformation: StringTransformer):
        self._command = command
        self._stdin = stdin
        self._transformation = transformation

    def applier(self, environment: ApplicationEnvironment) -> Program:
        return Program(self._command,
                       self._stdin,
                       self._transformation,
                       )


class ProgramDdv(DirDependentValue[ApplicationEnvironmentDependentValue[Program]]):
    def __init__(self,
                 command: CommandDdv,
                 stdin: StdinDataDdv,
                 transformation: StringTransformerDdv):
        self._command = command
        self._stdin = stdin
        self._transformation = transformation
        self._validators = (tuple(command.validators) + (transformation.validator(),))

    @property
    def command(self) -> CommandDdv:
        return self._command

    @property
    def stdin(self) -> StdinDataDdv:
        return self._stdin

    @property
    def transformation(self) -> StringTransformerDdv:
        return self._transformation

    @property
    def validators(self) -> Sequence[DdvValidator]:
        return self._validators

    @property
    def validator(self) -> DdvValidator:
        return ddv_validators.all_of(self._validators)

    def value_of_any_dependency(self, tcds: Tcds) -> ProgramAdv:
        return ProgramAdv(self.command.value_of_any_dependency(tcds),
                          self.stdin.value_of_any_dependency(tcds),
                          self.transformation.value_of_any_dependency(tcds))
