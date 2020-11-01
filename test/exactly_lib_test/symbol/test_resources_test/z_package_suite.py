import unittest

from exactly_lib_test.symbol.test_resources_test import symbol_usage_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        symbol_usage_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
