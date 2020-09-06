from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils import instruction_from_parts
from exactly_lib.instructions.multi_phase import sys_cmd
from exactly_lib.instructions.multi_phase.sys_cmd import TheInstructionDocumentationBase
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose, AssertPhasePurpose
from exactly_lib.util.textformat.structure.document import SectionContents


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(sys_cmd.parts_parser(instruction_name)),
        TheDocumentation(instruction_name))


class TheDocumentation(TheInstructionDocumentationBase, WithAssertPhasePurpose):
    def __init__(self, name: str):
        super().__init__(name, sys_cmd.SINGLE_LINE_DESCRIPTION_FOR_ASSERT_PHASE_INSTRUCTION)

    @property
    def assert_phase_purpose(self) -> AssertPhasePurpose:
        return AssertPhasePurpose.BOTH

    def outcome(self) -> SectionContents:
        return self._tp.section_contents(_OUTCOME)


_OUTCOME = """\
{PASS} if, and only if, the exit code from the program is 0.
"""
