import unittest

from exactly_lib_test.util.test_resources_test import symbol_table_assertions


def suite() -> unittest.TestSuite:
    return symbol_table_assertions.suite()
