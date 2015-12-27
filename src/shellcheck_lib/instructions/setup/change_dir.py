from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from shellcheck_lib.instructions.multi_phase_instructions import change_dir as cd_utils
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder

description = cd_utils.TheDescription


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        destination_directory = cd_utils.parse(source.instruction_argument)
        return _Instruction(destination_directory)


class _Instruction(SetupPhaseInstruction):
    def __init__(self, destination_directory: cd_utils.DestinationPath):
        self.destination_directory = destination_directory

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        error_message = cd_utils.change_dir(self.destination_directory,
                                            environment.eds)
        return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)
