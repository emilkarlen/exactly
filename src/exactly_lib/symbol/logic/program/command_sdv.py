from typing import Sequence

from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.logic.program.arguments_sdv import ArgumentsSdv
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.sdv_with_validation import DirDepValueResolverWithValidation
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.symbol.utils import DirDepValueResolver
from exactly_lib.test_case.validation import sdv_validation
from exactly_lib.test_case.validation.sdv_validation import SdvValidator
from exactly_lib.test_case_utils.program.command import arguments_sdvs
from exactly_lib.type_system.logic.program.command import CommandDdv, CommandDriverDdv
from exactly_lib.util.process_execution.command import Command
from exactly_lib.util.symbol_table import SymbolTable


class CommandDriverSdv(DirDepValueResolver[CommandDriverDdv]):
    """
    Resolves a :class:`CommandDriverDdv`,
    and supplies a validator of the ingredients involved.
    """

    def __init__(self, validators: Sequence[SdvValidator] = ()):
        self._validators = validators

    @property
    def validators(self) -> Sequence[SdvValidator]:
        return self._validators

    def resolve(self, symbols: SymbolTable) -> CommandDriverDdv:
        raise NotImplementedError('abstract method')

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')


class CommandSdv(DirDepValueResolverWithValidation[CommandDdv]):
    """
    Resolves a :class:`CommandDdv`,
    and supplies a validator of the ingredients involved.

    This class works a bit like a immutable builder of Command - new arguments
    may be appended to form a new object representing a different command.

    This is the way more complex commands are built from simpler ones.
    """

    def __init__(self,
                 command_driver: CommandDriverSdv,
                 arguments: ArgumentsSdv):
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
                          self._arguments.arguments_list.resolve(symbols))

    def resolve_of_any_dep(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        return self.resolve(environment.symbols).value_of_any_dependency(environment.tcds)

    @property
    def validator(self) -> SdvValidator:
        return sdv_validation.all_of(self.validators)

    @property
    def validators(self) -> Sequence[SdvValidator]:
        return tuple(self._driver.validators) + tuple(self._arguments.validators)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([
            self._driver,
            self._arguments])

    @property
    def arguments(self) -> ListSdv:
        return self._arguments.arguments_list
