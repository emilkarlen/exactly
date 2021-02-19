from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.multi_phase.timeout import parse, doc
from exactly_lib.impls.instructions.setup.utils import instruction_from_parts


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(parse.PARTS_PARSER),
        doc.TheInstructionDocumentation(instruction_name))
