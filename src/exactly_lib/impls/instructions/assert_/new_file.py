from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.assert_.utils import instruction_from_parts
from exactly_lib.impls.instructions.multi_phase.new_file import parse


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(parse.parts_parser(True)),
        parse.TheInstructionDocumentation(instruction_name, True))
