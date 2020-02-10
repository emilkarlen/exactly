from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolDefinition
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as instrs
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.test_case.result import sh


def setup_phase_instruction_that_defines_symbol(symbol_definition: SymbolDefinition) -> SetupPhaseInstruction:
    return _SetupPhaseInstructionThatSetsSymbol(symbol_definition)


class _SetupPhaseInstructionThatSetsSymbol(SetupPhaseInstruction):
    def __init__(self,
                 symbol_definition: SymbolDefinition):
        self.symbol_definition = symbol_definition

    def main(self,
             environment: instrs.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        environment.symbols.put(self.symbol_definition.name,
                                self.symbol_definition.symbol_container)
        return sh.new_sh_success()

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return [self.symbol_definition]
