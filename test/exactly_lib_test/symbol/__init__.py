import unittest

from exactly_lib_test.symbol import restriction, data, err_msg
from exactly_lib_test.symbol import test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        err_msg.suite(),
        restriction.suite(),
        data.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
