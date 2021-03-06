from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.multi_phase.define_symbol import instruction_setup
from exactly_lib.impls.instructions.setup.utils import instruction_from_parts


def setup(instruction_name: str) -> SingleInstructionSetup:
    return instruction_setup.setup(
        instruction_name,
        False,
        instruction_from_parts.Parser,
    )
