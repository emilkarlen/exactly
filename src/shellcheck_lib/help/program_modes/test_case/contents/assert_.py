from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseReference
from shellcheck_lib.help.utils.description import single_line_description


def phase_reference(phase_name: str) -> TestCasePhaseReference:
    return TestCasePhaseReference(single_line_description('The ' + phase_name + ' phase.'))
