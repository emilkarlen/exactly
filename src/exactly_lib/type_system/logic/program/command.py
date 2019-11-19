from abc import ABC

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.util.process_execution.command import Command, CommandDriver


class CommandDriverDdv(DirDependentValue[CommandDriver], ABC):
    pass


class CommandDdv(DirDependentValue[Command]):
    def __init__(self,
                 command_driver: CommandDriverDdv,
                 arguments: ListDdv):
        self._command_driver = command_driver
        self._arguments = arguments

    @property
    def command_driver(self) -> CommandDriverDdv:
        return self._command_driver

    @property
    def arguments(self) -> ListDdv:
        return self._arguments

    def value_of_any_dependency(self, tcds: Tcds) -> Command:
        return Command(self._command_driver.value_of_any_dependency(tcds),
                       self._arguments.value_of_any_dependency(tcds))
