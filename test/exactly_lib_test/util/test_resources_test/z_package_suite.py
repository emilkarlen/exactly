import unittest

from exactly_lib_test.util.test_resources_test import symbol_table_assertions, line_source_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        symbol_table_assertions.suite(),
        line_source_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
