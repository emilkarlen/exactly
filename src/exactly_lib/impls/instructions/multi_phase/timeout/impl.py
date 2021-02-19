from typing import Sequence, Optional

from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.types.integer.integer_sdv import IntegerSdv
from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.sdv import sdv_validation
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator, ConstantSuccessSdvValidator
from exactly_lib.util import functional
from exactly_lib.util.symbol_table import SymbolTable


class TheInstructionEmbryo(embryo.PhaseAgnosticInstructionEmbryo[None]):
    def __init__(self, value: Optional[IntegerSdv]):
        self._value = value

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return functional.reduce_optional(sdv_structure.get_references, (), self._value)

    @property
    def validator(self) -> SdvValidator:
        if self._value is None:
            return ConstantSuccessSdvValidator()

        def get_validator(symbols: SymbolTable) -> DdvValidator:
            return self._value.resolve(symbols).validator()

        return sdv_validation.SdvValidatorFromDdvValidator(get_validator)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             ):
        def resolve(x: Optional[IntegerSdv]) -> Optional[int]:
            return x.resolve(environment.symbols).value_of_any_dependency(environment.tcds)

        value = functional.reduce_optional(resolve, None, self._value)

        settings.set_timeout(value)
