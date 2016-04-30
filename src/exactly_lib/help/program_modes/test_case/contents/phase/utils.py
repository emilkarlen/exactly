from exactly_lib.execution import environment_variables
from exactly_lib.execution.execution_directory_structure import SUB_DIRECTORY__ACT
from exactly_lib.help.utils.formatting import SectionName
from exactly_lib.util.textformat.parse import normalize_and_parse


def pwd_at_start_of_phase_for_configuration_phase() -> list:
    return []


def pwd_at_start_of_phase_first_phase_executed_in_the_sandbox() -> list:
    return normalize_and_parse('At the beginning of the phase, the Present Working Directory (PWD) '
                               'is the %s/ sub directory of the sandbox.' % SUB_DIRECTORY__ACT)


def pwd_at_start_of_phase_for_non_first_phases() -> list:
    return normalize_and_parse("""\
    The Present Working Directory is the same as at the end of the previous phase.

    (which is the %s/ sub directory of the sandbox, if it has not been changed.)""" % SUB_DIRECTORY__ACT)


def env_vars_for_configuration_phase() -> list:
    return []


def env_vars_up_to_act__TODO_CHECK_THIS() -> list:
    return environment_variables.SET_AT_SETUP__ENV_VARS + environment_variables.SET_AT_EDS__ENV_VARS


def env_vars_after_act__TODO_CHECK_THIS() -> list:
    return env_vars_up_to_act__TODO_CHECK_THIS() + environment_variables.SET_AT_BEFORE_ASSERT__ENV_VARS


def sequence_info__succeeding_phase(phase_name_dictionary: dict,
                                    following_phase: SectionName) -> list:
    return normalize_and_parse(_SEQUENCE_INFO__SUCCEEDING_PHASE.format(phase=phase_name_dictionary,
                                                                       following_phase=following_phase))


_SEQUENCE_INFO__SUCCEEDING_PHASE = """\
If any of the instructions fail, the execution jumps to the {phase[cleanup]} phase,
and the test case halts with an error.

Otherwise, the {following_phase} phase follows.
"""
