import unittest

from exactly_lib_test.common import help, err_msg, result_reporting


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        err_msg.suite(),
        result_reporting.suite(),
        help.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
