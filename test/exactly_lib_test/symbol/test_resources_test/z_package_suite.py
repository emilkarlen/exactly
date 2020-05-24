import unittest

from exactly_lib_test.symbol.test_resources_test import container_assertions, \
    restrictions_assertions, sdv_assertions, symbol_usage_assertions, sdv_type_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        container_assertions.suite(),
        restrictions_assertions.suite(),
        sdv_assertions.suite(),
        symbol_usage_assertions.suite(),
        sdv_type_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
