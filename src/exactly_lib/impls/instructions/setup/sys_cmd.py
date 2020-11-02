from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.multi_phase import sys_cmd as sys_cmd_common
from exactly_lib.impls.instructions.setup.utils import instruction_from_parts


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(sys_cmd_common.parts_parser(instruction_name)),
        sys_cmd_common.DescriptionForNonAssertPhaseInstruction(instruction_name))
