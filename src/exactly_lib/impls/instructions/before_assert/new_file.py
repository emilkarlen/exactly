from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.before_assert.utils import instruction_from_parts
from exactly_lib.impls.instructions.multi_phase import new_file


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(new_file.parts_parser(True)),
        new_file.TheInstructionDocumentation(instruction_name))
