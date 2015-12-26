import subprocess

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.general.textformat.structure.paragraph import single_para
from shellcheck_lib.instructions.multi_phase_instructions.shell import TheDescriptionBase
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh


class TheDescription(TheDescriptionBase):
    def __init__(self, name: str):
        super().__init__(name)

    def main_description_rest(self) -> list:
        return single_para('The instruction is successful if (and only if) the exit code from the command is 0.')


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> CleanupPhaseInstruction:
        arguments = source.instruction_argument.strip()
        if not arguments:
            msg = 'Program to execute must be given as argument'
            raise SingleInstructionInvalidArgumentException(msg)
        return _ShellInstruction(arguments)


class _ShellInstruction(CleanupPhaseInstruction):
    def __init__(self,
                 command: str):
        self.command = command

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        exit_code = subprocess.call(self.command,
                                    shell=True)
        if exit_code != 0:
            return sh.new_sh_hard_error('Program finished with non-zero exit code {}'.format(exit_code))
        return sh.new_sh_success()
