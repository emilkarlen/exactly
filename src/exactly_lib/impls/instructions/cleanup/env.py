from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.cleanup.utils import instruction_from_parts
from exactly_lib.impls.instructions.multi_phase import env as env_instruction


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(env_instruction.PARTS_PARSER),
        env_instruction.TheInstructionDocumentation(instruction_name))