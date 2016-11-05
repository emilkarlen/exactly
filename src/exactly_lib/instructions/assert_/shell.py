from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils.instruction_from_parts import AssertPhaseInstructionFromValidatorAndExecutor
from exactly_lib.instructions.multi_phase_instructions import shell as shell_common
from exactly_lib.instructions.multi_phase_instructions.shell import TheInstructionDocumentationBase


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        shell_common.Parser(instruction_name, AssertPhaseInstructionFromValidatorAndExecutor),
        TheDescription(instruction_name))


class TheDescription(TheInstructionDocumentationBase):
    def __init__(self, name: str):
        super().__init__(name)

    def _main_description_rest_prelude(self) -> list:
        text = """\
            The assertion PASS if, and only if, the exit code from {COMMAND} is 0.

            All other exit codes makes the assertion FAIL.
            """
        return self._paragraphs(text)
