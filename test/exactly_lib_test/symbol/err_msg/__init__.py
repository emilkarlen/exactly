import unittest

from exactly_lib_test.symbol.err_msg import error_messages, restriction_failures


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        error_messages.suite(),
        restriction_failures.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
