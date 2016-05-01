from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from exactly_lib.instructions.multi_phase_instructions import new_file as new_file_utils
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            Parser(),
        new_file_utils.TheInstructionDocumentation(instruction_name))


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        argument = new_file_utils.parse(source)
        return _Instruction(argument)


class _Instruction(SetupPhaseInstruction):
    def __init__(self, file_info: new_file_utils.FileInfo):
        self.file_info = file_info

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        error_message = new_file_utils.create_file(self.file_info, environment.eds)
        return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)
