from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseHelp, \
    TestCasePhaseHelpForPhaseWithoutInstructions
from shellcheck_lib.help.utils.description import single_line_description


def phase_reference(phase_name: str) -> TestCasePhaseHelp:
    return TestCasePhaseHelpForPhaseWithoutInstructions(phase_name,
                                                        single_line_description('TODO The ' + phase_name + ' phase.'))
