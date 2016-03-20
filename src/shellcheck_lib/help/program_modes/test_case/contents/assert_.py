from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseInstructionSet
from shellcheck_lib.help.program_modes.test_case.phase_help_contents_structures import \
    TestCasePhaseHelpForPhaseWithInstructions, PhaseSequenceInfo
from shellcheck_lib.help.utils.description import Description, single_line_description
from shellcheck_lib.util.textformat.structure.paragraph import para


class AssertPhaseHelp(TestCasePhaseHelpForPhaseWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: TestCasePhaseInstructionSet):
        super().__init__(name, instruction_set)

    def purpose(self) -> Description:
        return single_line_description('TODO the purpose of the %s phase' % self._name_as_header)

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo([para('TODO before ' + self._name_as_header)],
                                 [para('TODO after ' + self._name_as_header)])

    def is_mandatory(self) -> bool:
        return False
