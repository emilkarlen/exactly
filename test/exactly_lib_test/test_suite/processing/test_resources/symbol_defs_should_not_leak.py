from typing import List, Sequence

from exactly_lib.appl_env.os_services import OsServices
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.test_case.result import sh
from exactly_lib_test.test_suite.processing.test_resources.instruction_utils import InstructionParserBase
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext


class Registry:
    def __init__(self):
        self.observation = None


class SetupPhaseInstructionThatDefinesSymbol(SetupPhaseInstruction):
    def __init__(self, name: str):
        self.name = name

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return [StringSymbolContext.of_constant(self.name, 'arbitrary value').definition]

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()


class SetupPhaseInstructionThatRegistersExistenceOfSymbol(SetupPhaseInstruction):
    def __init__(self,
                 registry: Registry,
                 symbol_to_observe: str):
        self.registry = registry
        self.env_var_to_observe = symbol_to_observe

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        self.registry.observation = environment.symbols.contains(self.env_var_to_observe)
        return sh.new_sh_success()


class InstructionParserForDefine(InstructionParserBase):
    def __init__(self):
        super().__init__(1)

    def _parse(self, args: List[str]) -> SetupPhaseInstruction:
        return SetupPhaseInstructionThatDefinesSymbol(args[0])


class InstructionParserForRegistersExistenceOfSymbol(InstructionParserBase):
    def __init__(self, registry: Registry):
        super().__init__(1)
        self.registry = registry

    def _parse(self, args: List[str]) -> SetupPhaseInstruction:
        return SetupPhaseInstructionThatRegistersExistenceOfSymbol(self.registry,
                                                                   args[0])
