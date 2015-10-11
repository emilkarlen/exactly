import subprocess

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib.test_case.os_services import OsServices

DESCRIPTION = Description(
    "Executes the given program using the system's shell.",
    'The instruction is successful if (and only if) the exit code from the command is 0.',
    [InvokationVariant('PROGRAM ARGUMENT...',
                       'A plain file.'),
     ])


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        arguments = source.instruction_argument.strip()
        if not arguments:
            msg = 'Program to execute must be given as argument'
            raise SingleInstructionInvalidArgumentException(msg)
        return _ShellInstruction(arguments)


class _ShellInstruction(SetupPhaseInstruction):
    def __init__(self,
                 command: str):
        self.command = command

    def pre_validate(self,
                     global_environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        exit_code = subprocess.call(self.command,
                                    shell=True)
        if exit_code != 0:
            return sh.new_sh_hard_error('Program finished with non-zero exit code {}'.format(exit_code))
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()
