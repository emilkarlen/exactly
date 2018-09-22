import unittest

from exactly_lib_test.type_system.logic import file_matcher, line_matcher
from exactly_lib_test.type_system.logic.string_transformer import z_package_suite as string_transformer
from exactly_lib_test.type_system.logic.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        line_matcher.suite(),
        file_matcher.suite(),
        string_transformer.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
