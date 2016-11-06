from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.before_assert.utils.instruction_from_parts import \
    BeforeAssertPhaseInstructionFromValidatorAndExecutor
from exactly_lib.instructions.multi_phase_instructions import run


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        run.instruction_parser(instruction_name, BeforeAssertPhaseInstructionFromValidatorAndExecutor),
        run.TheInstructionDocumentation(instruction_name,
                                        description_rest_text=run.NON_ASSERT_PHASE_DESCRIPTION_REST))
