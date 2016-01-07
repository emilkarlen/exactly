from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.instructions.multi_phase_instructions import shell as shell_common
from shellcheck_lib.instructions.multi_phase_instructions.shell import DescriptionForNonAssertPhaseInstruction
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.before_assert import BeforeAssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh


def description(instruction_name) -> Description:
    return DescriptionForNonAssertPhaseInstruction(instruction_name)


def parser() -> SingleInstructionParser:
    return shell_common.Parser(_ShellInstruction)


class _ShellInstruction(BeforeAssertPhaseInstruction):
    def __init__(self,
                 executor: shell_common.Executor):
        self.executor = executor

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase) -> sh.SuccessOrHardError:
        exit_code = self.executor.run()
        if exit_code != 0:
            return sh.new_sh_hard_error('Program finished with non-zero exit code {}'.format(exit_code))
        return sh.new_sh_success()
