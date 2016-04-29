from exactly_lib.section_document.syntax import section_header
from exactly_lib.execution import phases


def phase_header_line(phase: phases.Phase) -> str:
    return section_header(phase.section_name)
