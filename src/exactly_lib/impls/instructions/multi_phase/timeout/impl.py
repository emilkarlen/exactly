from typing import Sequence

from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.types.integer.integer_sdv import IntegerSdv
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.sdv import sdv_validation
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator
from exactly_lib.util.symbol_table import SymbolTable


class TheInstructionEmbryo(embryo.PhaseAgnosticInstructionEmbryo[None]):
    def __init__(self, value: IntegerSdv):
        self._value = value

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._value.references

    @property
    def validator(self) -> SdvValidator:
        def get_validator(symbols: SymbolTable) -> DdvValidator:
            return self._value.resolve(symbols).validator()

        return sdv_validation.SdvValidatorFromDdvValidator(get_validator)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             ):
        value = self._value.resolve(environment.symbols).value_of_any_dependency(environment.tcds)
        settings.set_timeout(value)
