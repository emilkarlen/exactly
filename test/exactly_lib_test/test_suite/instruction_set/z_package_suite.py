import unittest

from exactly_lib_test.test_suite.instruction_set import utils
from exactly_lib_test.test_suite.instruction_set.sections import z_package_suite as sections


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        utils.suite(),
        sections.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
