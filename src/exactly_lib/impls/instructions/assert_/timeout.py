from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.assert_.utils import instruction_from_parts
from exactly_lib.impls.instructions.multi_phase.timeout import parse, doc


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(parse.PARTS_PARSER),
        doc.TheInstructionDocumentation(instruction_name, is_in_assert_phase=True))
