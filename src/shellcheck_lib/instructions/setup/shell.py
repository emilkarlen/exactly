from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.instructions.multi_phase_instructions import shell as shell_common
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder


def description(instruction_name) -> Description:
    return shell_common.DescriptionForNonAssertPhaseInstruction(instruction_name)


def parser() -> SingleInstructionParser:
    return shell_common.Parser(_ShellInstruction)


class _ShellInstruction(SetupPhaseInstruction):
    def __init__(self,
                 executor: shell_common.Executor):
        self.executor = executor

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return shell_common.run_and_return_sh(self.executor)
