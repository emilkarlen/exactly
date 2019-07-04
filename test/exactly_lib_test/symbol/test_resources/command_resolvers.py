from typing import Sequence

from exactly_lib.symbol.logic.program.command_resolver import CommandDriverResolver
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.logic.program.command_value import CommandValue


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
