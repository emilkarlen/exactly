from exactly_lib.act_phase_setups import command_line
from exactly_lib.default.program_modes import test_suite
from exactly_lib.processing.preprocessor import IDENTITY_PREPROCESSOR
from exactly_lib.test_suite.suite_hierarchy_reading import Environment


def default_environment() -> Environment:
    return Environment(test_suite.new_parser(),
                       IDENTITY_PREPROCESSOR,
                       command_line.act_phase_setup())
