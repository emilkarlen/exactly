from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.before_assert.utils import instruction_from_parts
from exactly_lib.instructions.multi_phase import run


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(run.parts_parser(instruction_name)),
        run.TheInstructionDocumentation(instruction_name,
                                        description_rest_text=run.NON_ASSERT_PHASE_DESCRIPTION_REST))
