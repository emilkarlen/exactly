from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.assert_.utils import instruction_from_parts
from exactly_lib.impls.instructions.multi_phase import shell
from exactly_lib.impls.instructions.multi_phase.shell import TheInstructionDocumentationBase, \
    SINGLE_LINE_DESCRIPTION_FOR_ASSERT_PHASE_INSTRUCTION
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose, AssertPhasePurpose
from exactly_lib.util.textformat.structure.document import SectionContents


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(shell.parts_parser(instruction_name)),
        TheDocumentation(instruction_name))


class TheDocumentation(TheInstructionDocumentationBase, WithAssertPhasePurpose):
    def __init__(self, name: str):
        super().__init__(name,
                         phase_identifier.ASSERT.section_name,
                         SINGLE_LINE_DESCRIPTION_FOR_ASSERT_PHASE_INSTRUCTION)

    @property
    def assert_phase_purpose(self) -> AssertPhasePurpose:
        return AssertPhasePurpose.BOTH

    def outcome(self) -> SectionContents:
        return self._tp.section_contents(_OUTCOME)


_OUTCOME = """\
{PASS} iff the {EXIT_CODE} from {COMMAND} is 0.
"""
