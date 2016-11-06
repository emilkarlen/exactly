from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions import run
from exactly_lib.instructions.setup.utils.instruction_from_parts import SetupPhaseInstructionFromValidatorAndExecutor


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        run.instruction_parser(instruction_name, SetupPhaseInstructionFromValidatorAndExecutor),
        run.TheInstructionDocumentation(instruction_name,
                                        description_rest_text=run.NON_ASSERT_PHASE_DESCRIPTION_REST))
