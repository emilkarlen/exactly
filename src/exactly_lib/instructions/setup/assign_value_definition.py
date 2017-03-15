from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions import assign_value_definition
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.value_definition.value_structure import ValueDefinition2


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        assign_value_definition.TheInstructionDocumentation(instruction_name))


class Parser(InstructionParser):
    def parse(self, source: ParseSource) -> SetupPhaseInstruction:
        value_definition = assign_value_definition.parse(source)
        return _Instruction(value_definition)


class _Instruction(SetupPhaseInstruction):
    def __init__(self,
                 value_definition: ValueDefinition2):
        self.value_definition = value_definition

    def value_usages(self) -> list:
        return [self.value_definition]

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        environment.value_definitions.put(self.value_definition.name,
                                          self.value_definition.value_container)
        return sh.new_sh_success()
