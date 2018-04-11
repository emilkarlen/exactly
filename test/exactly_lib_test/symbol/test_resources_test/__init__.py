import unittest

from exactly_lib_test.symbol.test_resources_test import resolver_structure_assertions, \
    restrictions_assertions, resolver_assertions, symbol_usage_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        resolver_structure_assertions.suite(),
        restrictions_assertions.suite(),
        resolver_assertions.suite(),
        symbol_usage_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
