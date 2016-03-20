from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseHelp
from shellcheck_lib.util.textformat.structure import document as doc


def render_test_case_phase_overview(phase_help: TestCasePhaseHelp) -> doc.SectionContents:
    return phase_help.render()
