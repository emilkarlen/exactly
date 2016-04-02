import unittest

from shellcheck_lib_test.help.concepts import configuration_parameters


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        configuration_parameters.suite()
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
