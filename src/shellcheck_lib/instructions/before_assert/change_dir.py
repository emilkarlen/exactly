from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from shellcheck_lib.instructions.multi_phase_instructions import change_dir as cd_utils
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from shellcheck_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.phases.result import sh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            Parser(),
        cd_utils.TheInstructionDocumentation(instruction_name))


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> BeforeAssertPhaseInstruction:
        destination_directory = cd_utils.parse(source.instruction_argument)
        return _Instruction(destination_directory)


class _Instruction(BeforeAssertPhaseInstruction):
    def __init__(self, destination_directory: cd_utils.DestinationPath):
        self.destination_directory = destination_directory

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return cd_utils.execute_with_sh_result(self.destination_directory,
                                               environment.eds)
