import unittest

from exactly_lib.help.concepts.configuration_parameters import configuration_parameter as sut
from shellcheck_lib_test.help.concepts.test_resources import suite_for_configuration_parameter_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_configuration_parameter_documentation(sut.EXECUTION_MODE_CONFIGURATION_PARAMETER),
        suite_for_configuration_parameter_documentation(sut.HOME_DIRECTORY_CONFIGURATION_PARAMETER),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
