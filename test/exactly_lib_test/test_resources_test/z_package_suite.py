import unittest

from exactly_lib_test.test_resources_test import string_formatting
from exactly_lib_test.test_resources_test.source import z_package_suite as source
from exactly_lib_test.test_resources_test.value_assertions import z_package_suite as value_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        string_formatting.suite(),
        value_assertions.suite(),
        source.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
