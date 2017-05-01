from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions import assign_symbol
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.symbol.value_structure import ValueDefinition
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        assign_symbol.TheInstructionDocumentation(instruction_name))


class Parser(InstructionParser):
    def parse(self, source: ParseSource) -> SetupPhaseInstruction:
        symbol = assign_symbol.parse(source)
        return _Instruction(symbol)


class _Instruction(SetupPhaseInstruction):
    def __init__(self,
                 symbol: ValueDefinition):
        self.symbol = symbol

    def symbol_usages(self) -> list:
        return [self.symbol]

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        environment.symbols.put(self.symbol.name,
                                self.symbol.value_container)
        return sh.new_sh_success()
