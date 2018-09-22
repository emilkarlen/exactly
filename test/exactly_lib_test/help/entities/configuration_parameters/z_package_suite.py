import unittest

from exactly_lib_test.help.entities.configuration_parameters import render, all_configuration_parameters


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        render.suite(),
        all_configuration_parameters.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
