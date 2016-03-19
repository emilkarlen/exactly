from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from shellcheck_lib.instructions.multi_phase_instructions import new_dir as mkdir_utils
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from shellcheck_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.phases.result import sh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            Parser(),
        mkdir_utils.TheInstructionReference(instruction_name))


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> BeforeAssertPhaseInstruction:
        argument = mkdir_utils.parse(source.instruction_argument)
        return _Instruction(argument)


class _Instruction(BeforeAssertPhaseInstruction):
    def __init__(self, directory_components: str):
        self.directory_components = directory_components

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return mkdir_utils.execute_and_return_sh(self.directory_components)
