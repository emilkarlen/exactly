from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils import instruction_from_parts
from exactly_lib.instructions.multi_phase_instructions import run


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(run.parts_parser(instruction_name)),
        run.TheInstructionDocumentation(instruction_name,
                                        description_rest_text=run.ASSERT_PHASE_DESCRIPTION_REST))
