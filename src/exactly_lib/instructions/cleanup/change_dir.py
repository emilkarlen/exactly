from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions import change_dir as cd_utils
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        cd_utils.TheInstructionDocumentation(instruction_name, is_after_act_phase=True))


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> CleanupPhaseInstruction:
        destination_directory = cd_utils.parse(rest_of_line, is_after_act_phase=True)
        return _Instruction(destination_directory)


class _Instruction(CleanupPhaseInstruction):
    def __init__(self, destination_directory: cd_utils.DestinationPath):
        self.destination_directory = destination_directory

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             previous_phase: PreviousPhase) -> sh.SuccessOrHardError:
        return cd_utils.execute_with_sh_result(self.destination_directory,
                                               environment.sds)
