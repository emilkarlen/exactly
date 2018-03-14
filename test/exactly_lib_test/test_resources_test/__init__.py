import unittest

from exactly_lib_test.test_resources_test import string_formatting, value_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        string_formatting.suite(),
        value_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
