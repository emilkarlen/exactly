import unittest

from exactly_lib_test.symbol import restriction, data
from exactly_lib_test.symbol import test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        restriction.suite(),
        data.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
