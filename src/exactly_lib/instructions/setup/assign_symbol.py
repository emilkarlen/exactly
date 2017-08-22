from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions import assign_symbol
from exactly_lib.instructions.setup.utils import instruction_from_parts


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(assign_symbol.PARTS_PARSER),
        assign_symbol.TheInstructionDocumentation(instruction_name))
