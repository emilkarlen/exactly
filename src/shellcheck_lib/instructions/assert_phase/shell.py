import subprocess

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case.help.instruction_description import InvokationVariant, DescriptionWithConstantValues
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import pfh

DESCRIPTION = DescriptionWithConstantValues(
    "Executes the given program using the system's shell.",
    """The assertion PASSes if (and only if) the exit code from the command is 0.

    All other exit codes makes the assertion FAIL.
    """,
    [InvokationVariant('PROGRAM ARGUMENT...',
                       'A plain file.'),
     ])


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = source.instruction_argument.strip()
        if not arguments:
            msg = 'Program to execute must be given as argument'
            raise SingleInstructionInvalidArgumentException(msg)
        return _ShellInstruction(arguments)


class _ShellInstruction(AssertPhaseInstruction):
    def __init__(self,
                 command: str):
        self.command = command

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        exit_code = subprocess.call(self.command,
                                    shell=True)
        if exit_code != 0:
            return pfh.new_pfh_fail('Program finished with non-zero exit code {}'.format(exit_code))
        return pfh.new_pfh_pass()
