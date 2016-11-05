from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils.instruction_from_parts import AssertPhaseInstructionFromValidatorAndExecutor
from exactly_lib.instructions.multi_phase_instructions import run


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        run.InstructionParser2(instruction_name, AssertPhaseInstructionFromValidatorAndExecutor),
        run.TheInstructionDocumentation(instruction_name,
                                        "Runs a program and PASS if, and only if, its exit code is 0"))
