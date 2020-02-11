from abc import ABC
from typing import Sequence, TypeVar, Generic

from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.logic.program.arguments_sdv import ArgumentsSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references, \
    SymbolDependentValue
from exactly_lib.test_case_utils.program.command import arguments_sdvs
from exactly_lib.type_system.logic.program.command import CommandDdv, CommandDriverDdv, NonAppEnvDepComponentDdv
from exactly_lib.util.symbol_table import SymbolTable

PRIMITIVE = TypeVar('PRIMITIVE')


class NonAppEnvDepComponentSdv(Generic[PRIMITIVE], SymbolDependentValue, ABC):
    def resolve(self, symbols: SymbolTable) -> NonAppEnvDepComponentDdv[PRIMITIVE]:
        pass


class CommandDriverSdv(NonAppEnvDepComponentSdv[CommandDriverDdv]):
    pass


class CommandSdv(NonAppEnvDepComponentSdv[CommandDdv]):
    """
    This class works a bit like a immutable builder of Command - new arguments
    may be appended to form a new object representing a different command.

    This is the way more complex commands are built from simpler ones.
    """

    def __init__(self,
                 command_driver: CommandDriverSdv,
                 arguments: ArgumentsSdv,
                 ):
        self._driver = command_driver
        self._arguments = arguments

    def new_with_additional_arguments(self, additional_arguments: ArgumentsSdv) -> 'CommandSdv':
        """
        Creates a new SDV with additional arguments appended at the end of
        current argument list.
        """
        return CommandSdv(self._driver,
                          self._arguments.new_accumulated(additional_arguments))

    def new_with_additional_argument_list(self, additional_arguments: ListSdv) -> 'CommandSdv':
        return self.new_with_additional_arguments(arguments_sdvs.new_without_validation(additional_arguments))

    def resolve(self, symbols: SymbolTable) -> CommandDdv:
        return CommandDdv(self._driver.resolve(symbols),
                          self._arguments.resolve(symbols),
                          )

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([
            self._driver,
            self._arguments])
