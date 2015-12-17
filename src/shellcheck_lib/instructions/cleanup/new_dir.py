from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from shellcheck_lib.instructions.multi_phase_instructions import new_dir as mkdir_utils
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh

DESCRIPTION = mkdir_utils.DESCRIPTION


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> CleanupPhaseInstruction:
        argument = mkdir_utils.parse(source.instruction_argument)
        return _Instruction(argument)


class _Instruction(CleanupPhaseInstruction):
    def __init__(self, directory_components: str):
        self.directory_components = directory_components

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        error_message = mkdir_utils.make_dir_in_current_dir(self.directory_components)
        return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)
