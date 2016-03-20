from shellcheck_lib.help.program_modes.test_case.contents.phase_help_contents_structures import \
    TestCasePhaseHelpForPhaseWithInstructions
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseHelp, \
    TestCasePhaseInstructionSet
from shellcheck_lib.help.utils.description import single_line_description


def phase_reference(phase_name: str,
                    instruction_set: TestCasePhaseInstructionSet) -> TestCasePhaseHelp:
    return TestCasePhaseHelpForPhaseWithInstructions(phase_name,
                                                     single_line_description('TODO The ' + phase_name + ' phase.'),
                                                     instruction_set)
