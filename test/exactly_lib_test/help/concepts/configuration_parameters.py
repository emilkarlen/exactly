import unittest

import exactly_lib.help.concepts.configuration_parameters.execution_mode
import exactly_lib.help.concepts.configuration_parameters.home_directory
from exactly_lib.help.concepts.configuration_parameters import all_configuration_parameters as sut
from exactly_lib_test.help.concepts.test_resources import suite_for_configuration_parameter_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_configuration_parameter_documentation(
            exactly_lib.help.concepts.configuration_parameters.execution_mode.EXECUTION_MODE_CONFIGURATION_PARAMETER),
        suite_for_configuration_parameter_documentation(
            exactly_lib.help.concepts.configuration_parameters.home_directory.HOME_DIRECTORY_CONFIGURATION_PARAMETER),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
