from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase import run
from exactly_lib.instructions.setup.utils import instruction_from_parts


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(run.parts_parser(instruction_name)),
        run.TheInstructionDocumentation(instruction_name,
                                        run.NON_ASSERT_PHASE_SINGLE_LINE_DESCRIPTION,
                                        description_rest_text=run.NON_ASSERT_PHASE_DESCRIPTION_REST))
