from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCasePhaseHelp
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.paragraph import para


def render_test_case_phase_overview(phase_help: TestCasePhaseHelp) -> doc.SectionContents:
    description = phase_help.reference.description
    return doc.SectionContents([para(description.single_line_description)] +
                               description.rest,
                               [])
