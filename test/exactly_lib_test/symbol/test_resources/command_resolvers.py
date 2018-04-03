from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.program.command_resolver import CommandDriverResolver
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.logic.program.command_value import CommandValue
from exactly_lib.util.symbol_table import SymbolTable


class CommandDriverResolverForConstantTestImpl(CommandDriverResolver):
    def __init__(self,
                 constant_value: CommandValue,
                 validators: Sequence[PreOrPostSdsValidator] = ()):
        super().__init__(validators)
        self._validators = validators
        self._constant_value = constant_value

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return self._validators

    def make(self,
             symbols: SymbolTable,
             arguments: ListResolver) -> CommandValue:
        return self._constant_value
