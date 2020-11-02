from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.cleanup.utils import instruction_from_parts
from exactly_lib.impls.instructions.multi_phase import run


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(run.parts_parser(instruction_name)),
        run.TheInstructionDocumentation(instruction_name,
                                        run.NON_ASSERT_PHASE_SINGLE_LINE_DESCRIPTION,
                                        outcome=run.NON_ASSERT_PHASE_OUTCOME))
