import unittest

from exactly_lib_test.symbol import restriction_failures
from exactly_lib_test.symbol import symbol_syntax, error_messages
from exactly_lib_test.symbol import symbol_usage
from exactly_lib_test.symbol.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        symbol_usage.suite(),
        symbol_syntax.suite(),
        error_messages.suite(),
        restriction_failures.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
