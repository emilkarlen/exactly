from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.before_assert.utils.instruction_from_parts import \
    BeforeAssertPhaseInstructionFromValidatorAndExecutor
from exactly_lib.instructions.multi_phase_instructions import run
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        parser(instruction_name),
        run.TheInstructionDocumentation(instruction_name,
                                        description_rest_text=run.NON_ASSERT_PHASE_DESCRIPTION_REST))


def parser(instruction_name: str) -> SingleInstructionParser:
    return run.InstructionParser2(instruction_name,
                                  BeforeAssertPhaseInstructionFromValidatorAndExecutor)
