from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.cleanup.utils.instruction_from_parts import \
    CleanupPhaseInstructionFromValidatorAndExecutor
from exactly_lib.instructions.multi_phase_instructions import shell as shell_common
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        parser(instruction_name),
        shell_common.DescriptionForNonAssertPhaseInstruction(instruction_name))


def parser(instruction_name: str) -> SingleInstructionParser:
    return shell_common.Parser2(instruction_name,
                                CleanupPhaseInstructionFromValidatorAndExecutor)
