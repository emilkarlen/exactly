import unittest

from exactly_lib_test.test_case_utils.condition import instruction
from exactly_lib_test.test_case_utils.condition.integer import z_package_suite as integer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        instruction.suite(),
        integer.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
