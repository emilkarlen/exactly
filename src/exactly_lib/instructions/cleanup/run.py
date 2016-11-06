from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.cleanup.utils.instruction_from_parts import \
    instruction_info_for
from exactly_lib.instructions.multi_phase_instructions import run


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        run.instruction_parser(instruction_info_for(instruction_name)),
        run.TheInstructionDocumentation(instruction_name,
                                        description_rest_text=run.NON_ASSERT_PHASE_DESCRIPTION_REST))
