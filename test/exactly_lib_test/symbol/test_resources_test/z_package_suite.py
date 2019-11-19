import unittest

from exactly_lib_test.symbol.test_resources_test import sdv_structure_assertions, \
    restrictions_assertions, sdv_assertions, symbol_usage_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        sdv_structure_assertions.suite(),
        restrictions_assertions.suite(),
        sdv_assertions.suite(),
        symbol_usage_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
