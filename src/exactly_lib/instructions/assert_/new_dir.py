from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions import new_dir as mkdir_utils
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.value_definition.concrete_values import FileRefResolver


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        mkdir_utils.TheInstructionDocumentation(instruction_name, is_in_assert_phase=True))


class Parser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> AssertPhaseInstruction:
        argument = mkdir_utils.parse(rest_of_line)
        return _Instruction(argument)


class _Instruction(AssertPhaseInstruction):
    def __init__(self, destination_path_resolver: FileRefResolver):
        self.destination_path_resolver = destination_path_resolver

    def main(self, environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        error_message = mkdir_utils.make_dir_in_current_dir(environment.path_resolving_environment,
                                                            self.destination_path_resolver)
        return pfh.new_pfh_pass() if error_message is None else pfh.new_pfh_hard_error(error_message)
