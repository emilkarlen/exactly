from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions import new_dir as mkdir_utils
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.value_definition.concrete_values import FileRefResolver


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        mkdir_utils.TheInstructionDocumentation(instruction_name))


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> BeforeAssertPhaseInstruction:
        argument = mkdir_utils.parse(rest_of_line)
        return _Instruction(argument)


class _Instruction(BeforeAssertPhaseInstruction):
    def __init__(self, dir_path_resolver: FileRefResolver):
        self.dir_path_resolver = dir_path_resolver

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return mkdir_utils.execute_and_return_sh(environment.path_resolving_environment, self.dir_path_resolver)
