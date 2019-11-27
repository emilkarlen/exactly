from typing import Sequence

from exactly_lib.symbol.logic.program.command_sdv import CommandDriverSdv
from exactly_lib.test_case.validation.sdv_validation import SdvValidator
from exactly_lib.type_system.logic.program.command import CommandDdv


class CommandDriverSdvForConstantTestImpl(CommandDriverSdv):
    def __init__(self,
                 constant_ddv: CommandDdv,
                 validators: Sequence[SdvValidator] = ()):
        super().__init__(validators)
        self._validators = validators
        self._constant_ddv = constant_ddv

    @property
    def validators(self) -> Sequence[SdvValidator]:
        return self._validators
