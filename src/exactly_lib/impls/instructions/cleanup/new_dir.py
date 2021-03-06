from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.cleanup.utils import instruction_from_parts
from exactly_lib.impls.instructions.multi_phase import new_dir as new_dir_utils


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(new_dir_utils.PARTS_PARSER),
        new_dir_utils.TheInstructionDocumentation(instruction_name))
