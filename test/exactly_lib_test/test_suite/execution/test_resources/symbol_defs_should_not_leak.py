from typing import List, Sequence

from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.test_case.result import sh
from exactly_lib_test.symbol.test_resources.symbol_utils import definition_with_arbitrary_element
from exactly_lib_test.test_suite.execution.test_resources.instruction_utils import InstructionParserBase


class Registry:
    def __init__(self):
        self.observation = None


class SetupPhaseInstructionThatDefinesSymbol(SetupPhaseInstruction):
    def __init__(self, name: str):
        self.name = name

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return [definition_with_arbitrary_element(self.name)]

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
