from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from shellcheck_lib.instructions.multi_phase_instructions import new_file as new_file_utils
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder

description = new_file_utils.TheDescription


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> SetupPhaseInstruction:
        argument = new_file_utils.parse(source)
        return _Instruction(argument)


class _Instruction(SetupPhaseInstruction):
    def __init__(self, file_info: new_file_utils.FileInfo):
        self.file_info = file_info

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        error_message = new_file_utils.create_file(self.file_info, environment.eds)
        return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)
