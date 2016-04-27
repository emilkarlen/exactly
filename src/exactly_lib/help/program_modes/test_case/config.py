from exactly_lib.execution import phases


def phase_help_name(phase: phases.Phase) -> str:
    return phase.identifier
