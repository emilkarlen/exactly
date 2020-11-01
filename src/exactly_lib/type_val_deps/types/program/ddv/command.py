from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import DirDependentValue
from exactly_lib.type_val_deps.types.list_.list_ddv import ListDdv
from exactly_lib.type_val_deps.types.program.ddv.argument import ArgumentsDdv
from exactly_lib.type_val_prims.description.structure_building import StructureBuilder
from exactly_lib.type_val_prims.program.command import Command, CommandDriver

PRIMITIVE = TypeVar('PRIMITIVE')


class NonAppEnvDepComponentDdv(Generic[PRIMITIVE], DirDependentValue[PRIMITIVE], ABC):
    @property
    def validators(self) -> Sequence[DdvValidator]:
        return ()


class CommandDriverDdv(NonAppEnvDepComponentDdv[CommandDriver], ABC):
    @abstractmethod
    def structure_for(self, arguments: ListDdv) -> StructureBuilder:
        """:returns A new object on each invokation."""
        pass


class CommandDdv(NonAppEnvDepComponentDdv[Command]):
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

    def structure(self) -> StructureBuilder:
        """:returns A new object on each invokation."""
        return self._command_driver.structure_for(self._arguments.arguments_list)

    @property
    def validators(self) -> Sequence[DdvValidator]:
        return self._validators

    @property
    def command_driver(self) -> CommandDriverDdv:
        return self._command_driver

    def value_of_any_dependency(self, tcds: TestCaseDs) -> Command:
        return Command(self._command_driver.value_of_any_dependency(tcds),
                       self._arguments.value_of_any_dependency(tcds))
