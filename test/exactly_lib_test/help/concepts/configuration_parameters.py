import unittest

from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
from exactly_lib.help.concepts.configuration_parameters.execution_mode import EXECUTION_MODE_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.configuration_parameters.timeout import TIMEOUT_CONFIGURATION_PARAMETER
from exactly_lib_test.help.concepts.test_resources.test_case_impls import \
    suite_for_configuration_parameter_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_configuration_parameter_documentation(EXECUTION_MODE_CONFIGURATION_PARAMETER),
        suite_for_configuration_parameter_documentation(HOME_DIRECTORY_CONFIGURATION_PARAMETER),
        suite_for_configuration_parameter_documentation(ACTOR_CONCEPT),
        suite_for_configuration_parameter_documentation(TIMEOUT_CONFIGURATION_PARAMETER),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
