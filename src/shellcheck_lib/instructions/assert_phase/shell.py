from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.instructions.multi_phase_instructions import shell as shell_common
from shellcheck_lib.instructions.multi_phase_instructions.shell import TheDescriptionBase
from shellcheck_lib.instructions.utils.sub_process_execution import ExecuteInfo
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.phases.result import pfh
from shellcheck_lib.util.textformat import parse as text_parse


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            parser(),
            TheDescription(instruction_name))


class TheDescription(TheDescriptionBase):
    def __init__(self, name: str):
        super().__init__(name)

    def main_description_rest(self) -> list:
        text = """\
            The assertion PASSes if (and only if) the exit code from the command is 0.

            All other exit codes makes the assertion FAIL.
            """
        return text_parse.normalize_and_parse(text)


def parser() -> SingleInstructionParser:
    return shell_common.Parser('instruction-name',
                               _ShellInstruction)


class _ShellInstruction(AssertPhaseInstruction):
    def __init__(self,
                 execute_info: ExecuteInfo):
        self.execute_info = execute_info

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return shell_common.run_and_return_pfh(self.execute_info, environment.phase_logging)
