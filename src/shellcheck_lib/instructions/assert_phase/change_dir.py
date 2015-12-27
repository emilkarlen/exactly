from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from shellcheck_lib.instructions.multi_phase_instructions import change_dir as cd_utils
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import pfh

description = cd_utils.TheDescription


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        destination_directory = cd_utils.parse(source.instruction_argument)
        return _Instruction(destination_directory)


class _Instruction(AssertPhaseInstruction):
    def __init__(self, destination_directory: cd_utils.DestinationPath):
        self.destination_directory = destination_directory

    def main(self, environment: GlobalEnvironmentForPostEdsPhase, os_services: OsServices) -> pfh.PassOrFailOrHardError:
        error_message = cd_utils.change_dir(self.destination_directory,
                                            environment.eds)
        return pfh.new_pfh_pass() if error_message is None else pfh.new_pfh_hard_error(error_message)
