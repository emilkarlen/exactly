from abc import ABC

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.util.process_execution.command import Command, CommandDriver


class CommandDriverValue(DirDependentValue[CommandDriver], ABC):
    pass


class CommandValue(DirDependentValue[Command]):
    def __init__(self,
                 command_driver: CommandDriverValue,
                 arguments: ListDdv):
        self._command_driver = command_driver
        self._arguments = arguments

    @property
    def command_driver(self) -> CommandDriverValue:
        return self._command_driver

    @property
    def arguments(self) -> ListDdv:
        return self._arguments

    def value_of_any_dependency(self, tcds: HomeAndSds) -> Command:
        return Command(self._command_driver.value_of_any_dependency(tcds),
                       self._arguments.value_of_any_dependency(tcds))
