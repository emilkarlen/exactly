from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.execution import phases
from shellcheck_lib.instructions.multi_phase_instructions import shell as shell_common
from shellcheck_lib.instructions.utils.sub_process_execution import InstructionMetaInfo, ExecuteInfo
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction, PreviousPhase
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            parser(instruction_name),
            shell_common.DescriptionForNonAssertPhaseInstruction(instruction_name))


def parser(instruction_name: str) -> SingleInstructionParser:
    return shell_common.Parser(InstructionMetaInfo(phases.CLEANUP.identifier,
                                                   instruction_name),
                               _ShellInstruction)


class _ShellInstruction(CleanupPhaseInstruction):
    def __init__(self,
                 execute_info: ExecuteInfo):
        self.execute_info = execute_info

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             previous_phase: PreviousPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return shell_common.run_and_return_sh(self.execute_info, environment.eds)
