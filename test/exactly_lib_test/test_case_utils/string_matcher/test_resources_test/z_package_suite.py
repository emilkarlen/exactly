import unittest

from . import integration_check_test


def suite() -> unittest.TestSuite:
    return integration_check_test.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
