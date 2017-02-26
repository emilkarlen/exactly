import unittest

from exactly_lib_test.test_suite.instruction_set.sections import configuration, cases, suites


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        configuration.suite(),
        cases.suite(),
        suites.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
