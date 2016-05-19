from exactly_lib.act_phase_setups import single_command_setup
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.test_suite.suite_hierarchy_reading import Environment


def default_environment() -> Environment:
    return Environment(IDENTITY_PREPROCESSOR,
                       single_command_setup.act_phase_setup())
