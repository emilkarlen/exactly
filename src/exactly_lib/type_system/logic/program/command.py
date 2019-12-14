from abc import ABC
from typing import Sequence

from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.program.argument import ArgumentsDdv
from exactly_lib.util.process_execution.command import Command, CommandDriver


class CommandDriverDdv(DirDependentValue[CommandDriver], ABC):

    @property
    def validators(self) -> Sequence[DdvValidator]:
        return ()


class CommandDdv(DirDependentValue[Command]):
    def __init__(self,
                 command_driver: CommandDriverDdv,
                 arguments: ArgumentsDdv,
                 ):
        self._command_driver = command_driver
        self._arguments = arguments
        self._validators = (
                tuple(command_driver.validators)
                +
                tuple(arguments.validators)
        )

    @property
    def validators(self) -> Sequence[DdvValidator]:
        return self._validators

    @property
    def command_driver(self) -> CommandDriverDdv:
        return self._command_driver

    def value_of_any_dependency(self, tcds: Tcds) -> Command:
        return Command(self._command_driver.value_of_any_dependency(tcds),
                       self._arguments.value_of_any_dependency(tcds))
