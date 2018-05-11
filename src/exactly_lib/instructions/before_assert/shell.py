from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.before_assert.utils import instruction_from_parts
from exactly_lib.instructions.multi_phase import shell as shell_common


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(shell_common.parts_parser(instruction_name)),
        shell_common.DescriptionForNonAssertPhaseInstruction(instruction_name))
