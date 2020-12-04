from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.multi_phase.new_file import parse
from exactly_lib.impls.instructions.setup.utils import instruction_from_parts


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(parse.parts_parser(False)),
        parse.TheInstructionDocumentation(instruction_name, False),
    )
