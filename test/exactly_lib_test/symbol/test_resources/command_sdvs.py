from typing import Sequence

from exactly_lib.symbol.logic.program.command_sdv import CommandDriverSdv
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.logic.program.command import CommandDdv


class CommandDriverSdvForConstantTestImpl(CommandDriverSdv):
    def __init__(self,
                 constant_ddv: CommandDdv,
                 validators: Sequence[PreOrPostSdsValidator] = ()):
        super().__init__(validators)
        self._validators = validators
        self._constant_ddv = constant_ddv

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return self._validators
