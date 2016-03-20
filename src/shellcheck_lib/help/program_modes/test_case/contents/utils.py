from shellcheck_lib.execution import environment_variables
from shellcheck_lib.execution.execution_directory_structure import SUB_DIRECTORY__ACT
from shellcheck_lib.util.textformat.parse import normalize_and_parse


def pwd_at_start_of_phase_for_configuration_phase() -> list:
    return []


def pwd_at_start_of_phase_for_non_first_phases() -> list:
    return normalize_and_parse("""\
    TODO PWD is what the phase before set it to.
    Or the %s/ sub directory of the sandbox.""" % SUB_DIRECTORY__ACT)


def env_vars_for_configuration_phase() -> list:
    return []


def env_vars_up_to_act__TODO_CHECK_THIS() -> list:
    return environment_variables.SET_AT_SETUP__ENV_VARS + environment_variables.SET_AT_EDS__ENV_VARS


def env_vars_after_act__TODO_CHECK_THIS() -> list:
    return env_vars_up_to_act__TODO_CHECK_THIS() + environment_variables.SET_AT_ASSERT__ENV_VARS
