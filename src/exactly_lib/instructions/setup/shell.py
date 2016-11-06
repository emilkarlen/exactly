from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions import shell as shell_common
from exactly_lib.instructions.setup.utils.instruction_from_parts import instruction_info_for


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        shell_common.instruction_parser(instruction_info_for(instruction_name)),
        shell_common.DescriptionForNonAssertPhaseInstruction(instruction_name))
