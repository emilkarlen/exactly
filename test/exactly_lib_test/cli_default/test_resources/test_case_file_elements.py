from exactly_lib.section_document.syntax import section_header
from exactly_lib.test_case import phase_identifier


def phase_header_line(phase: phase_identifier.Phase) -> str:
    return section_header(phase.section_name)
