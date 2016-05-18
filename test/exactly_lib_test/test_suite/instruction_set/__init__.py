import unittest

from exactly_lib_test.test_suite.instruction_set.sections import configuration


def suite() -> unittest.TestSuite:
    return configuration.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
