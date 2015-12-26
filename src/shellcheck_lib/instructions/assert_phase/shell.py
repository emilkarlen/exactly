from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.general.textformat import parse as text_parse
from shellcheck_lib.instructions.multi_phase_instructions import shell as shell_common
from shellcheck_lib.instructions.multi_phase_instructions.shell import TheDescriptionBase
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import pfh


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
    return shell_common.Parser(_ShellInstruction)


class _ShellInstruction(AssertPhaseInstruction):
    def __init__(self,
                 executor: shell_common.Executor):
        self.executor = executor

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        exit_code = self.executor.run()
        if exit_code != 0:
            return pfh.new_pfh_fail('Program finished with non-zero exit code {}'.format(exit_code))
        return pfh.new_pfh_pass()
