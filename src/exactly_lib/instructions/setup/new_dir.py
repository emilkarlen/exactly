from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions import new_dir as new_dir_utils
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.symbol.concrete_values import FileRefResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        new_dir_utils.TheInstructionDocumentation(instruction_name, may_use_symbols=True))


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> SetupPhaseInstruction:
        argument = new_dir_utils.parse(rest_of_line, may_use_symbols=True)
        return _Instruction(argument)


class _Instruction(SetupPhaseInstruction):
    def __init__(self, dir_path_resolver: FileRefResolver):
        self.dir_path_resolver = dir_path_resolver

    def symbol_usages(self) -> list:
        return self.dir_path_resolver.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return new_dir_utils.execute_and_return_sh(environment.path_resolving_environment, self.dir_path_resolver)
