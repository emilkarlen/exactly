from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.general.textformat.structure.paragraph import single_para
from shellcheck_lib.instructions.multi_phase_instructions import shell as shell_common
from shellcheck_lib.instructions.multi_phase_instructions.shell import TheDescriptionBase
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder


class TheDescription(TheDescriptionBase):
    def __init__(self, name: str):
        super().__init__(name)

    def main_description_rest(self) -> list:
        return single_para('The instruction is successful if (and only if) the exit code from the command is 0.')


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
