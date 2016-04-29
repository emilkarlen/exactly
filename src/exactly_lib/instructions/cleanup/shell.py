from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from exactly_lib.instructions.multi_phase_instructions import shell as shell_common
from exactly_lib.instructions.utils.sub_process_execution import ExecuteInfo
from exactly_lib.test_case.instruction_setup import SingleInstructionSetup
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from exactly_lib.test_case.phases.result import sh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            parser(instruction_name),
            shell_common.DescriptionForNonAssertPhaseInstruction(instruction_name))


def parser(instruction_name: str) -> SingleInstructionParser:
    return shell_common.Parser(instruction_name,
                               _ShellInstruction)


class _ShellInstruction(CleanupPhaseInstruction):
    def __init__(self,
                 execute_info: ExecuteInfo):
        self.execute_info = execute_info

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             previous_phase: PreviousPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return shell_common.run_and_return_sh(self.execute_info, environment.phase_logging)
