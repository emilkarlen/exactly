from exactly_lib.execution import environment_variables
from exactly_lib.execution.execution_directory_structure import SUB_DIRECTORY__ACT
from exactly_lib.execution.execution_mode import NAME_SKIP
from exactly_lib.help.concepts.configuration_parameters.execution_mode import EXECUTION_MODE_CONFIGURATION_PARAMETER
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


def env_vars_up_to_act() -> list:
    return environment_variables.SET_AT_SETUP__ENV_VARS + environment_variables.SET_AT_EDS__ENV_VARS


def env_vars_after_act() -> list:
    return env_vars_up_to_act() + environment_variables.SET_AT_BEFORE_ASSERT__ENV_VARS


def sequence_info__not_executed_if_execution_mode_is_skip() -> list:
    return normalize_and_parse(_SEQUENCE_INFO__NOT_EXECUTED_IF_EXECUTION_MODE_IS_SKIP.format(
        execution_mode=EXECUTION_MODE_CONFIGURATION_PARAMETER.name().singular,
        SKIP=NAME_SKIP,
    ))


def sequence_info__succeeding_phase(phase_name_dictionary: dict,
                                    following_phase: SectionName) -> list:
    return normalize_and_parse(_SEQUENCE_INFO__SUCCEEDING_PHASE.format(phase=phase_name_dictionary,
                                                                       following_phase=following_phase))


_SEQUENCE_INFO__SUCCEEDING_PHASE = """\
If any of the instructions fail, the execution jumps to the {phase[cleanup]} phase,
and the test case halts with an error.

Otherwise, the {following_phase} phase follows.
"""


def sequence_info__preceding_phase(following_phase: SectionName) -> list:
    return normalize_and_parse(_SEQUENCE_INFO__PRECEDING_PHASE.format(following_phase=following_phase))


_SEQUENCE_INFO__PRECEDING_PHASE = """\
This phase is executed directly after the {following_phase} phase.
"""

_SEQUENCE_INFO__NOT_EXECUTED_IF_EXECUTION_MODE_IS_SKIP = """\
If the {execution_mode} is set to {SKIP}, then this phase is not executed.

Otherwise:
"""
