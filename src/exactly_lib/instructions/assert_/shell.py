from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils import instruction_from_parts
from exactly_lib.instructions.multi_phase_instructions import shell
from exactly_lib.instructions.multi_phase_instructions.shell import TheInstructionDocumentationBase, \
    SINGLE_LINE_DESCRIPTION_FOR_ASSERT_PHASE_INSTRUCTION
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose, AssertPhasePurpose


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(shell.parts_parser(instruction_name)),
        TheDocumentation(instruction_name))


class TheDocumentation(TheInstructionDocumentationBase, WithAssertPhasePurpose):
    def __init__(self, name: str):
        super().__init__(name, SINGLE_LINE_DESCRIPTION_FOR_ASSERT_PHASE_INSTRUCTION)

    @property
    def assert_phase_purpose(self) -> AssertPhasePurpose:
        return AssertPhasePurpose.BOTH

    def _main_description_rest_prelude(self) -> list:
        text = """\
            The assertion PASS if, and only if, the exit code from {COMMAND} is 0.

            All other exit codes makes the assertion FAIL.
            """
        return self._paragraphs(text)
