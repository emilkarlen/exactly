from exactly_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from exactly_lib.instructions.multi_phase_instructions import new_dir as mkdir_utils
from exactly_lib.test_case.instruction_setup import SingleInstructionSetup
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from exactly_lib.test_case.phases.result import sh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            Parser(),
        mkdir_utils.TheInstructionDocumentation(instruction_name))


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> CleanupPhaseInstruction:
        argument = mkdir_utils.parse(source.instruction_argument)
        return _Instruction(argument)


class _Instruction(CleanupPhaseInstruction):
    def __init__(self, directory_components: str):
        self.directory_components = directory_components

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             previous_phase: PreviousPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        error_message = mkdir_utils.make_dir_in_current_dir(self.directory_components)
        return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)
