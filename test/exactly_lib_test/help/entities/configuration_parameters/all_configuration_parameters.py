import unittest

from exactly_lib.help.entities.configuration_parameters.all_configuration_parameters import all_configuration_parameters
from exactly_lib_test.help.entities.configuration_parameters.test_resources import \
    suite_for_configuration_parameter_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_configuration_parameter_documentation(doc)
        for doc in all_configuration_parameters()
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
