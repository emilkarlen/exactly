from typing import Set

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue, DirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.util.process_execution.command import Command, CommandDriver


class CommandDriverValue(DirDependentValue[CommandDriver]):
    pass


class CommandValue(MultiDirDependentValue[Command]):
    def __init__(self,
                 command_driver: CommandDriverValue,
                 arguments: ListValue):
        self._command_driver = command_driver
        self._arguments = arguments

    @property
    def command_driver(self) -> CommandDriverValue:
        return self._command_driver

    @property
    def arguments(self) -> ListValue:
        return self._arguments

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._command_driver.resolving_dependencies().union(self._arguments.resolving_dependencies())

    def value_when_no_dir_dependencies(self) -> Command:
        return Command(self._command_driver.value_when_no_dir_dependencies(),
                       self._arguments.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> Command:
        return Command(self._command_driver.value_of_any_dependency(home_and_sds),
                       self._arguments.value_of_any_dependency(home_and_sds))
