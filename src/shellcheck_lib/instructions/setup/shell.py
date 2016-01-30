from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.instructions.multi_phase_instructions import shell as shell_common
from shellcheck_lib.instructions.utils.sub_process_execution import ExecuteInfo
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            parser(instruction_name),
            shell_common.DescriptionForNonAssertPhaseInstruction(instruction_name))


def parser(instruction_name: str) -> SingleInstructionParser:
    return shell_common.Parser(instruction_name,
                               _ShellInstruction)


class _ShellInstruction(SetupPhaseInstruction):
    def __init__(self,
                 execute_info: ExecuteInfo):
        self.execute_info = execute_info

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return shell_common.run_and_return_sh(self.execute_info, environment.phase_logging)
