from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.before_assert.utils import instruction_from_parts
from exactly_lib.instructions.multi_phase import define_symbol


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(define_symbol.PARTS_PARSER),
        define_symbol.TheInstructionDocumentation(instruction_name))
